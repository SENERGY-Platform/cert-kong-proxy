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

client_secret = os.environ.get('CLIENT_SECRET')
if not client_secret:
    raise Exception('client certificate missing')


def get_user_token(cert):
    KEYCLOAK_URL = os.environ.get('KEYCLOAK_URL')
    KEYCLOAK_REALM = os.environ.get('KEYCLOAK_REALM')

    user_name = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    auth_data = {
        'client_id': os.environ.get('CLIENT_ID'),
        'client_secret': client_secret,
        'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'requested_subject': user_name
    }
    auth_url = f'{KEYCLOAK_URL}/auth/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token'
    response = requests.post(auth_url, data=auth_data)
    token = response.json()
    return token['access_token']

def make_request(token):
    full_path = request.full_path
    gateway_url = os.environ.get('GATEWAY_URL')

    target_url = urllib.parse.urljoin(gateway_url, full_path)
    headers = {
        'Authorization': f'Bearer {token}'
    }
    # Get raw request data, could be of any type
    data = request.get_data()

    method = request.headers.get('Request-Method')
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

    # the PEM cert wil contain URL encoded characters like %20 for spaces
    decoded_pem_cert = urllib.parse.unquote(pem_cert)
    cert = x509.load_pem_x509_certificate(decoded_pem_cert.encode(), default_backend())

    if not cert:
        return {'error': 'SSL certificate missing'}

    token = get_user_token(cert)
    return make_request(token)

    