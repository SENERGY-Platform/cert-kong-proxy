<a href="https://github.com/SENERGY-Platform/cert-kong-proxy/actions/workflows/tests.yml" rel="nofollow">
    <img src="https://github.com/SENERGY-Platform/cert-kong-proxy/actions/workflows/tests.yml/badge.svg" alt="Tests" />
</a>

<a href="https://github.com/SENERGY-Platform/cert-kong-proxy/actions/workflows/deploy_dev.yml" rel="nofollow">
    <img src="https://github.com/SENERGY-Platform/cert-kong-proxy/actions/workflows/deploy_dev.yml/badge.svg" alt="Deployment Dev" />
</a>

# CERT-KONG-PROXY
This web server acts a reverse proxy which gets authenticated request from the cert-auth-proxy and exchanges a JWT token to forward the request to the backend

# Build
```
docker build -t cert-kong-proxy .
```

# Deployment
This service is exposed at port `443`. 

## Environment variables
- `CA_URL`: URL to the certificate authority for OCSP requests
- `CLIENT_SECRET=secret`: Keycloak client secret for token exchange 
- `CLIENT_ID=client`:  Keycloak client id for token exchange
- `GATEWAY_URL=http://gateway:8080`: URL to the API gateway to forward requests  
- `KEYCLOAK_URL=http://keycloak:8080`: URL to Keycloak 