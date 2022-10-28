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
```
docker run -p 443:443 \
            -e CLIENT_SECRET=secret \
            -e CLIENT_ID=client \
            -e GATEWAY_URL=http://gateway:8080 \
            -e KEYCLOAK_URL=http://keycloak:8080 \
            cert-kong-proxy 
```