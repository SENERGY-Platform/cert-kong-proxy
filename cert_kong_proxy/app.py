from flask import Flask
from flask import request
import os 
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
import urllib.parse
import requests 
import urllib.parse

app = Flask(__name__)

CLIENT_SECRET = os.environ.get('CLIENT_SECRET', 'secret')
KEYCLOAK_URL = os.environ.get('KEYCLOAK_URL', 'http://keycloak:8080')
KEYCLOAK_REALM = os.environ.get('KEYCLOAK_REALM', 'master')
CLIENT_ID = os.environ.get('CLIENT_ID', 'client')
GATEWAY_URL = os.environ.get('GATEWAY_URL', 'http://gateway:8080')

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

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def hello(path):
    pem_cert = request.headers.get('X-SSL-CERT')
    if not pem_cert:
        return {'error': 'SSL certificate missing'}, 400

    # the PEM cert wil contain URL encoded characters like %20 for spaces
    try:
        decoded_pem_cert = urllib.parse.unquote(pem_cert)
        cert = x509.load_pem_x509_certificate(decoded_pem_cert.encode(), default_backend())
    except Exception as e:
        return {'error': 'SSL certificate could not be parsed'}, 400

    cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    if len(cn) == 0:
        return {'error': 'Missing common name field'}, 400

    method = request.headers.get('Request-Method')
    if not method:
        return {'error': 'Missing request method header'}, 400

    token = get_user_token(cert)
    return make_request(token, method)

    
