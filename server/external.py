import requests

def get_ocsp(target_url, cert):
    return requests.post(target_url, json={"certificate": cert, "status": "good"})

def get_token(auth_url, auth_data):
    return requests.post(auth_url, data=auth_data)

def forward_request(method, target_url, headers, data):
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

    return response