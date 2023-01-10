from unittest import mock
import unittest
import os 
import json
from copy import deepcopy

os.environ['CLIENT_SECRET'] = "test"
os.environ['CLIENT_ID'] = "test"
os.environ['KEYCLOAK_REALM'] = "test"
os.environ['GATEWAY_URL'] = "test"
os.environ['KEYCLOAK_URL'] = "auth"
os.environ['CA_URL'] = "test"

from server.main import app

from helper import VALID_CERT,  get_good_ocsp, get_valid_token

class SuccessCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.valid_headers = {
            'X-SSL-CERT': VALID_CERT
        }

    @mock.patch('server.main.get_token', side_effect=get_valid_token)
    @mock.patch('server.main.get_ocsp', side_effect=get_good_ocsp)
    @mock.patch('server.main.forward_request', side_effect=get_good_ocsp)
    def test_get(self, mock_post, mock_get, mock_ocsp):
        headers = deepcopy(self.valid_headers)
        headers['Request-Method'] = 'GET'
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, 200)

    @mock.patch('server.main.get_token', side_effect=get_valid_token)
    @mock.patch('server.main.get_ocsp', side_effect=get_good_ocsp)
    @mock.patch('server.main.forward_request', side_effect=get_good_ocsp)
    def test_post(self, mock_post, mock_get, mock_ocsp):
        headers = deepcopy(self.valid_headers)
        headers['Request-Method'] = 'POST'
        response = self.client.post("/", headers=headers)
        self.assertEqual(response.status_code, 200)
    
    @mock.patch('server.main.get_token', side_effect=get_valid_token)
    @mock.patch('server.main.get_ocsp', side_effect=get_good_ocsp)
    @mock.patch('server.main.forward_request', side_effect=get_good_ocsp)
    def test_delete(self, mock_post, mock_get, mock_ocsp):
        headers = deepcopy(self.valid_headers)
        headers['Request-Method'] = 'DELETE'
        response = self.client.delete("/", headers=headers)
        self.assertEqual(response.status_code, 200)
    
    @mock.patch('server.main.get_token', side_effect=get_valid_token)
    @mock.patch('server.main.get_ocsp', side_effect=get_good_ocsp)
    @mock.patch('server.main.forward_request', side_effect=get_good_ocsp)
    def test_path(self, mock_post, mock_get, mock_ocsp):
        headers = deepcopy(self.valid_headers)
        headers['Request-Method'] = 'PATCH'
        response = self.client.patch("/", headers=headers)
        self.assertEqual(response.status_code, 200)

    @mock.patch('server.main.get_token', side_effect=get_valid_token)
    @mock.patch('server.main.get_ocsp', side_effect=get_good_ocsp)
    @mock.patch('server.main.forward_request', side_effect=get_good_ocsp)
    def test_head(self, mock_post, mock_get, mock_ocsp):
        headers = deepcopy(self.valid_headers)
        headers['Request-Method'] = 'HEAD'
        response = self.client.head("/", headers=headers)
        self.assertEqual(response.status_code, 200)

    @mock.patch('server.main.get_token', side_effect=get_valid_token)
    @mock.patch('server.main.get_ocsp', side_effect=get_good_ocsp)
    @mock.patch('server.main.forward_request', side_effect=get_good_ocsp)
    def test_put(self, mock_post, mock_get, mock_ocsp):
        headers = deepcopy(self.valid_headers)
        headers['Request-Method'] = 'PUT'
        response = self.client.put("/", headers=headers)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()