from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base config."""
    FLASK_ENV = environ.get('ENV', 'production')
    DEBUG = environ.get('DEBUG', False)
    TESTING = environ.get('TESTING', False)

    CLIENT_SECRET = environ['CLIENT_SECRET']
    CLIENT_ID = environ['CLIENT_ID']
    KEYCLOAK_REALM = environ['KEYCLOAK_REALM']
    GATEWAY_URL = environ['GATEWAY_URL']
    KEYCLOAK_URL = environ['KEYCLOAK_URL']
    CA_URL = environ['CA_URL']