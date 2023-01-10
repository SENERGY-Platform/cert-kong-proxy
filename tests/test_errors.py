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

from helper import VALID_CERT, get_revoked_ocsp, get_good_ocsp, get_invalid_token, get_valid_token, get_error_ocsp, get_invalid_ocsp_response

class ErrorMessagesCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

        # Valid certificate has a common name field and is urlencoded
        self.valid_headers = {
            'X-SSL-CERT': VALID_CERT
        }
        
    
    def test_get_missing_cert(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.data), {'error': 'SSL certificate missing'})

    def test_get_invalid_cert(self):
        invalid_headers = {
            'X-SSL-CERT': """-----BEGIN%20CERTIFICATE-----%0AMIIFazC0000000CA1OgAwIBAgIUIHZZhQSazpA9JqPOtHrk9iAPX%2BkwDQYJKoZIhvcNAQEL%0ABQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM%0AGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0yMjExMDIxNTM1MjZaFw0yMzEx%0AMDIxNTM1MjZaMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw%0AHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggIiMA0GCSqGSIb3DQEB%0AAQUAA4ICDwAwggIKAoICAQDNxFhaFSjDxm2GnZ3E7udXtCmG9zA7B%2Bllbta8kdWz%0A8Mwx2CKXR9lejnvKnhEPi3FzyEkdLxpndJqI%2Bdd/GviM6Kn3f2l3l4iFrNW/3vsx%0AOA%2Bc0FkIKF3kUP1G4NZctRjoSRFNPj5c8jzoD7syr6dqKVCyXfkDTnL6u5Ebe0o8%0ATn12SO5I%2B37kg5u9WtHpCBhNtDasTbAkc41uMRgecx31wVj2JMKSWQ48qroRYpxr%0A4YlYXMo%2BgZQ2%2BWQkbpjJBwsKEdMYZWpdtbvQOGEf47CdRjr9NYyzFTBiYsSwvU2B%0AkK4y7TjunQiy8Ml01p8TlVvWOPdla5mJo8KAQ3eua//oKI8SstjzA3HuUJTVN4Ha%0AUBY6D93KcEy4UyWAjXzUTpNjNjOf55UlrXDus9xxzWRTOk9fwVYB0adsorsIXeSw%0ALPefudu94YjP7IXFNf8bqSHC91ILDQeIjymQX7J%2BHTwUZNPv8Wc3p4YbQCXsLeKy%0APdkb3srPrf3tiXgupGUXGOPjDHYCO53UmbXrPMddP20Jv/izysZ%2BDE8fhq9J1rnV%0AqIXDO0MT3KcQbnICBbAkQMh5b7B5Tg3hkFnFNnlnxbPC63RupFTYLmdVaWA%2BWjxM%0AkVEdgyN69taSWt/qpTvE%2B6oxM%2Bq4bkfP63NxCBGRXKXm7G%2BKg2eSruZjgJ5K87P9%0A/QIDAQABo1MwUTAdBgNVHQ4EFgQUDjKLfWtxOGhR8IhTzokb0z%2BCcZowHwYDVR0j%0ABBgwFoAUDjKLfWtxOGhR8IhTzokb0z%2BCcZowDwYDVR0TAQH/BAUwAwEB/zANBgkq%0AhkiG9w0BAQsFAAOCAgEAj32Tzs8HcE/wxAjfGSoJ/cqVRTKk2PeW8qB5LfVYQo82%0AYtxq67RmKnUy4p9DcPy1WDxpFPYjPoQqD01w3RfCTWeJyY9xa/MHLoM%2BqkURX0kl%0AqSGrH8m/%2BNejWu4rDhOXfbQetVbdUhpKe/cGvxMyeLLdKD2ZdcvN0uxdHZ9D5791%0ALWhr335txPyB/PGDCFx2FEE/VIGcDWBD%2BBulC4GQ77LHt8l%2BDCiuDbJ/FhCD%2BR3f%0ASXpNynJ0MyC8zG/Ze7ejutOvxsZALxeSTdpDeBGH8CJY9uvITy6ZdsB3QkZ9DVi8%0A/Cx%2BdXkVPGVBdYs%2BK5LNBHL7QgWAC2quLxt7mFidC%2BGQlij2wMUO%2B2DM1LJOCeEy%0AKZ17FPZiki%2BuEMRMbS8n5GIhsLernoz4IILn5uTj7lr/yd95TJYhM4chXNcfJuZ6%0AuEREZs9v5/KKrCvWPPwoi3wYRE0kxDaBu5Do50kZmT092PloD%2BMi8UphKA7LluhC%0AkiJuID2nPa/JxRFRKBm1netgVRYstuv13REecR7WBQclbuVEo31%2BiED7OWMFdxdn%0Ar2BeIQ6ddhJUiQJdBj2j1/lDqBBNYQsmIZsuVgYwGFb5wA/8C8b8N8ND7XJBAZRj%0A58xvWjhSufBT2fgjYowndLvAzxJ3V%2BGR7LK7BvAKsvaFzducRBrQve6oU7RsHe8%3D%0A-----END%20CERTIFICATE-----"""
        }
        response = self.client.get("/", headers=invalid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.data), {'error': 'SSL certificate could not be parsed'})

    def test_get_missing_cn(self):
        invalid_headers = {
            'X-SSL-CERT': """-----BEGIN%20CERTIFICATE-----%0AMIIFazCCA1OgAwIBAgIUIHZZhQSazpA9JqPOtHrk9iAPX%2BkwDQYJKoZIhvcNAQEL%0ABQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM%0AGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0yMjExMDIxNTM1MjZaFw0yMzEx%0AMDIxNTM1MjZaMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw%0AHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggIiMA0GCSqGSIb3DQEB%0AAQUAA4ICDwAwggIKAoICAQDNxFhaFSjDxm2GnZ3E7udXtCmG9zA7B%2Bllbta8kdWz%0A8Mwx2CKXR9lejnvKnhEPi3FzyEkdLxpndJqI%2Bdd/GviM6Kn3f2l3l4iFrNW/3vsx%0AOA%2Bc0FkIKF3kUP1G4NZctRjoSRFNPj5c8jzoD7syr6dqKVCyXfkDTnL6u5Ebe0o8%0ATn12SO5I%2B37kg5u9WtHpCBhNtDasTbAkc41uMRgecx31wVj2JMKSWQ48qroRYpxr%0A4YlYXMo%2BgZQ2%2BWQkbpjJBwsKEdMYZWpdtbvQOGEf47CdRjr9NYyzFTBiYsSwvU2B%0AkK4y7TjunQiy8Ml01p8TlVvWOPdla5mJo8KAQ3eua//oKI8SstjzA3HuUJTVN4Ha%0AUBY6D93KcEy4UyWAjXzUTpNjNjOf55UlrXDus9xxzWRTOk9fwVYB0adsorsIXeSw%0ALPefudu94YjP7IXFNf8bqSHC91ILDQeIjymQX7J%2BHTwUZNPv8Wc3p4YbQCXsLeKy%0APdkb3srPrf3tiXgupGUXGOPjDHYCO53UmbXrPMddP20Jv/izysZ%2BDE8fhq9J1rnV%0AqIXDO0MT3KcQbnICBbAkQMh5b7B5Tg3hkFnFNnlnxbPC63RupFTYLmdVaWA%2BWjxM%0AkVEdgyN69taSWt/qpTvE%2B6oxM%2Bq4bkfP63NxCBGRXKXm7G%2BKg2eSruZjgJ5K87P9%0A/QIDAQABo1MwUTAdBgNVHQ4EFgQUDjKLfWtxOGhR8IhTzokb0z%2BCcZowHwYDVR0j%0ABBgwFoAUDjKLfWtxOGhR8IhTzokb0z%2BCcZowDwYDVR0TAQH/BAUwAwEB/zANBgkq%0AhkiG9w0BAQsFAAOCAgEAj32Tzs8HcE/wxAjfGSoJ/cqVRTKk2PeW8qB5LfVYQo82%0AYtxq67RmKnUy4p9DcPy1WDxpFPYjPoQqD01w3RfCTWeJyY9xa/MHLoM%2BqkURX0kl%0AqSGrH8m/%2BNejWu4rDhOXfbQetVbdUhpKe/cGvxMyeLLdKD2ZdcvN0uxdHZ9D5791%0ALWhr335txPyB/PGDCFx2FEE/VIGcDWBD%2BBulC4GQ77LHt8l%2BDCiuDbJ/FhCD%2BR3f%0ASXpNynJ0MyC8zG/Ze7ejutOvxsZALxeSTdpDeBGH8CJY9uvITy6ZdsB3QkZ9DVi8%0A/Cx%2BdXkVPGVBdYs%2BK5LNBHL7QgWAC2quLxt7mFidC%2BGQlij2wMUO%2B2DM1LJOCeEy%0AKZ17FPZiki%2BuEMRMbS8n5GIhsLernoz4IILn5uTj7lr/yd95TJYhM4chXNcfJuZ6%0AuEREZs9v5/KKrCvWPPwoi3wYRE0kxDaBu5Do50kZmT092PloD%2BMi8UphKA7LluhC%0AkiJuID2nPa/JxRFRKBm1netgVRYstuv13REecR7WBQclbuVEo31%2BiED7OWMFdxdn%0Ar2BeIQ6ddhJUiQJdBj2j1/lDqBBNYQsmIZsuVgYwGFb5wA/8C8b8N8ND7XJBAZRj%0A58xvWjhSufBT2fgjYowndLvAzxJ3V%2BGR7LK7BvAKsvaFzducRBrQve6oU7RsHe8%3D%0A-----END%20CERTIFICATE-----"""
        }
        response = self.client.get("/", headers=invalid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.data), {'error': 'Missing common name field'})

    def test_missing_request_method(self):
        response = self.client.get("/", headers=self.valid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.data), {'error': 'Missing request method header'})

    @mock.patch('server.main.get_token', side_effect=get_invalid_token)
    @mock.patch('server.main.get_ocsp', side_effect=get_good_ocsp)
    def test_keycloak_missing_token(self, mock1, mock2):
        headers = deepcopy(self.valid_headers)
        headers['Request-Method'] = 'GET'
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.data), {'error': 'Could not get token from keycloak'})

    @mock.patch('server.main.get_ocsp', side_effect=get_revoked_ocsp)
    def test_revoked_certificate(self, mock):
        headers = deepcopy(self.valid_headers)
        headers['Request-Method'] = 'GET'
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.data), {'error': 'Certificate is not valid'})


    @mock.patch('server.main.get_ocsp', side_effect=get_invalid_ocsp_response)
    def test_invalid_ocsp_response(self, mock):
        headers = deepcopy(self.valid_headers)
        headers['Request-Method'] = 'GET'
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.data), {'error': "Parsing of OCSP response was not successful"})
    
    @mock.patch('server.main.get_ocsp', side_effect=get_error_ocsp)
    def test_error_ocsp_request(self, mock):
        headers = deepcopy(self.valid_headers)
        headers['Request-Method'] = 'GET'
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.data), {'error': "Requesting OCSP status was not successful"})
        