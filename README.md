<div align="center">
    <a href="https://github.com/SENERGY-Platform/cert-kong-proxy/actions/workflows/test_and_coverage.yml" rel="nofollow">
        <img src="https://github.com/SENERGY-Platform/cert-kong-proxy/actions/workflows/test_and_coverage.yml/badge.svg" alt="Tests" />
    </a>
</div>

# CERT-KONG-PROXY
This web server acts a reverse proxy which gets authenticated request from the cert-auth-proxy and exchanges a JWT token to forward the request to the backend

# Build
```
docker build -t cert-kong-proxy .
```

# Deployment
Port 443 
CA_URL
CLIENT_SECRET=secret 
CLIENT_ID=client 
GATEWAY_URL=http://gateway:8080 
KEYCLOAK_URL=http://keycloak:8080 