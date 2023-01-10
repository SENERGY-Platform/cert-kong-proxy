from flask import Flask, request, jsonify
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from cryptography.x509 import ocsp
import base64
import urllib.parse
import requests 
import urllib.parse
from server.config import Config
import logging 
from server.external import get_ocsp, get_token, forward_request

app = Flask(__name__)

app.config.from_object(Config)
app.logger.setLevel(logging.DEBUG)

class APIError(Exception):
    """All custom API Exceptions"""
    pass

@app.errorhandler(APIError)
def handle_http_exception(e):
    app.logger.error(e)
    return jsonify({'error': str(e)}), 500

@app.after_request
def after_request(response):
    app.logger.info(f"{request.remote_addr} - {request.method} - {request.scheme} - {request.full_path} - {response.status}")
    app.logger.debug(f'Request body: {request.get_data()}')
    return response

def get_user_token(cert):
    user_name = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    auth_data = {
        'client_id': app.config["CLIENT_ID"],
        'client_secret': app.config["CLIENT_SECRET"],
        'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'requested_subject': user_name
    }
    auth_url = f'{app.config["KEYCLOAK_URL"]}/auth/realms/{app.config["KEYCLOAK_REALM"]}/protocol/openid-connect/token'
    response = get_token(auth_url, auth_data)
    data = response.json()
    if 'access_token' not in data:
        app.logger.debug(data)
        raise APIError(f'Could not get token from keycloak')
    return data['access_token']

def make_request(token, method):
    full_path = request.full_path

    target_url = urllib.parse.urljoin(app.config["GATEWAY_URL"], full_path)
    headers = {
        'Authorization': f'Bearer {token}'
    }
    # Get raw request data, could be of any type
    data = request.get_data()
    response = forward_request(method, target_url, headers, data)
    return response.content

def make_ocsp_request(cert):
    target_url = urllib.parse.urljoin(app.config["CA_URL"], 'ocsp')
    response = get_ocsp(target_url, cert)
    response_data = response.json()
    if not response_data['success']:
        err = response_data['errors']
        app.logger.debug(err)
        raise APIError(f'Requesting OCSP status was not successful')
    return response_data

def check_validity_of_cert(cert):
    response = make_ocsp_request(cert)

    try:  
        ocsp_response = response['result']['ocspResponse']
        ocsp_response_decoded = base64.b64decode(ocsp_response)
        ocsp_response_decoded = ocsp.load_der_ocsp_response(ocsp_response_decoded)
        app.logger.debug(ocsp_response_decoded.certificate_status)
        return ocsp_response_decoded.certificate_status == ocsp.OCSPCertStatus.GOOD
    except Exception as e:
        app.logger.error(e)
        raise APIError(f'Parsing of OCSP response was not successful')

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'DELETE', 'PATCH', 'PUT', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'DELETE', 'PATCH', 'PUT', 'HEAD'])
def hello(path):
    pem_cert = request.headers.get('X-SSL-CERT')
    if not pem_cert:
        raise APIError('SSL certificate missing')

    app.logger.debug(pem_cert)

    # the PEM cert wil contain URL encoded characters like %20 for spaces
    try:
        decoded_pem_cert = urllib.parse.unquote(pem_cert)
        cert = x509.load_pem_x509_certificate(decoded_pem_cert.encode(), default_backend())
    except Exception as e:
        app.logger.error(e)
        raise APIError(f'SSL certificate could not be parsed')

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

    
