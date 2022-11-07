from flask import Flask, request, jsonify
import os 
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from cryptography.x509 import ocsp
import base64
import urllib.parse
import requests 
import urllib.parse
from werkzeug.exceptions import HTTPException


app = Flask(__name__)

CLIENT_SECRET = os.environ.get('CLIENT_SECRET', 'secret')
KEYCLOAK_URL = os.environ.get('KEYCLOAK_URL', 'http://keycloak:8080')
KEYCLOAK_REALM = os.environ.get('KEYCLOAK_REALM', 'master')
CLIENT_ID = os.environ.get('CLIENT_ID', 'client')
GATEWAY_URL = os.environ.get('GATEWAY_URL', 'http://gateway:8080')
CA_URL = os.environ.get('CA_URL', 'http://gateway:8080')

class APIError(Exception):
    """All custom API Exceptions"""
    pass

@app.errorhandler(APIError)
def handle_http_exception(e):
    app.logger.error(e)
    return jsonify({'error': str(e)}), 500

def get_user_token(cert):
    user_name = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    auth_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'requested_subject': user_name
    }
    auth_url = f'{KEYCLOAK_URL}/auth/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token'
    response = requests.post(auth_url, data=auth_data)
    token = response.json()
    return token['access_token']

def make_request(token, method):
    full_path = request.full_path

    target_url = urllib.parse.urljoin(GATEWAY_URL, full_path)
    headers = {
        'Authorization': f'Bearer {token}'
    }
    # Get raw request data, could be of any type
    data = request.get_data()

    if method == 'GET':
        response = requests.get(target_url, headers=headers)
    elif method == 'POST':
        response = requests.post(target_url, data=data, headers=headers)
    elif method == 'DELETE':
        response = requests.delete(target_url, headers=headers)
    elif method == 'PATCH':
        response = requests.patch(target_url, data=data, headers=headers)
    elif method == 'PUT':
        response = requests.put(target_url, data=data, headers=headers)
    elif method == 'HEAD':
        response = requests.head(target_url, headers=headers)

    return response.content

def make_ocsp_request(cert):
    target_url = urllib.parse.urljoin(CA_URL, 'ocsp')
    response = requests.post(target_url, json={"certificate": cert, "status": "good"})
    response_data = response.json()
    if not response_data['success']:
        raise APIError('OCSP validation was not successful')
    return response_data

def check_validity_of_cert(cert):
    response = make_ocsp_request(cert)

    try:   
        ocsp_response_decoded = base64.b64decode(response.json()['result']['ocspResponse'])
        ocsp_response_decoded = ocsp.load_der_ocsp_response(ocsp_response_decoded)
        return ocsp_response_decoded.certificate_status == ocsp.OCSPCertStatus.GOOD
    except Exception as e:
        raise APIError('OCSP parsing was not successful')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def hello(path):
    pem_cert = request.headers.get('X-SSL-CERT')
    if not pem_cert:
        raise APIError('SSL certificate missing')

    # the PEM cert wil contain URL encoded characters like %20 for spaces
    try:
        decoded_pem_cert = urllib.parse.unquote(pem_cert)
        cert = x509.load_pem_x509_certificate(decoded_pem_cert.encode(), default_backend())
    except Exception as e:
        raise APIError('SSL certificate could not be parsed')

    cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    if len(cn) == 0:
        raise APIError('Missing common name field')

    method = request.headers.get('Request-Method')
    if not method:
        raise APIError('Missing request method header')

    cert_is_valid = check_validity_of_cert(decoded_pem_cert)

    if cert_is_valid:
        token = get_user_token(cert)
        return make_request(token, method)
    else:
        raise APIError('Certificate is not valid')

    
