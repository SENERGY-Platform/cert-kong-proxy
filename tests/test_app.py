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

# This method will be used by the mock to replace requests.get
def mocked_requests(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.content = json.dumps(json_data)
            
        def json(self):
            return self.json_data

    url = args[0]
    if 'auth' in url:
        return MockResponse({"access_token": "token"}, 200)
    else:
        return MockResponse({"key2": "value2"}, 200)

def mock_bad_ocsp(*args, **kwargs):
    return {"success": True, "result": {"ocspResponse": "MIIBpgoBAKCCAZ8wggGbBgkrBgEFBQcwAQEEggGMMIIBiDCCAS2hgY0wgYoxCzAJBgNVBAYTAkdCMRAwDgYDVQQIEwdFbmdsYW5kMQ8wDQYDVQQHEwZMb25kb24xFzAVBgNVBAoTDkN1c3RvbSBXaWRnZXRzMR0wGwYDVQQLExRDdXN0b20gV2lkZ2V0cyBIb3N0czEgMB4GA1UEAxMXaG9zdC5jdXN0b20td2lkZ2V0cy5jb20YDzIwMjIxMTA3MTYxMjAwWjCBiTCBhjBNMAkGBSsOAwIaBQAEFPrV+RrWDPtgcbhxno6XvaaV361kBBTn+cMADvAY8MArXNbSGJHbm7hFiAIUPesGbRICmm6SRHdDZF+tVCw8UE6hERgPMjAyMjExMDcxNjEyNTdaGA8yMDIyMTEwNzE2MDAwMFqgERgPMjAyMjExMDcxNjAwMDBaMAoGCCqGSM49BAMCA0kAMEYCIQCXA/4MhEytd3e89KwOygJa85SXAZRH5uF7yl0bsWIfvAIhAK3F8vobTHfh4c4bAu59F1Am2A70D5NYo6PF2/7fAz6w"}}

def mock_good_ocsp(*args, **kwargs):
    return {"success": True, "result": {"ocspResponse": "MIIBkgoBAKCCAYswggGHBgkrBgEFBQcwAQEEggF4MIIBdDCCARqhgY0wgYoxCzAJBgNVBAYTAkdCMRAwDgYDVQQIEwdFbmdsYW5kMQ8wDQYDVQQHEwZMb25kb24xFzAVBgNVBAoTDkN1c3RvbSBXaWRnZXRzMR0wGwYDVQQLExRDdXN0b20gV2lkZ2V0cyBIb3N0czEgMB4GA1UEAxMXaG9zdC5jdXN0b20td2lkZ2V0cy5jb20YDzIwMjIxMTA3MTQ1OTAwWjB3MHUwTTAJBgUrDgMCGgUABBT61fka1gz7YHG4cZ6Ol72mld+tZAQU5/nDAA7wGPDAK1zW0hiR25u4RYgCFCfFxWhLdjmXN51pWcBDRYPl82/XgAAYDzIwMjIxMTA3MTQwMDAwWqARGA8yMDIyMTEwNzE0MDAwMFowCgYIKoZIzj0EAwIDSAAwRQIhAJi2F84DmS/TxLwikTH9LM/vzKipvPLipWFRtatsM+VsAiBVk0hxd0ENHKyP5IbXd3Fc/ifIRW6NU8AnikoQmNJPiw=="}}

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

        # Valid certificate has a common name field and is urlencoded
        self.valid_headers = {
            'X-SSL-CERT': '-----BEGIN%20CERTIFICATE-----%0AMIIFiTCCA3GgAwIBAgIUAlplxT/x5EsyVV8%2BR/Dz9aqRQpYwDQYJKoZIhvcNAQEL%0ABQAwVDELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM%0AGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDENMAsGA1UEAwwEdXNlcjAeFw0yMjEx%0AMDMxMTA5NTZaFw0yMzExMDMxMTA5NTZaMFQxCzAJBgNVBAYTAkFVMRMwEQYDVQQI%0ADApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQx%0ADTALBgNVBAMMBHVzZXIwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQC1%0A6StfmZUfskoLxLIfO18tSJ7nO%2B0fGlnevVi58nohyHEeG0XH7K3GALipP43WOCHZ%0A91a17783Anea/YD0gtrbgjCoLjTcxGdRMFCQcSG3YsB95DKz4%2BFtu9%2BqxQloaQ82%0AknkjDugyXSPJcLDauyNklRR5tsJv6MroBO1uJYaLCHFPBdV9UxBOTnikcpLZzTBu%0Ab4UxJAJta4DZrhlQNij2/HL%2BGbcJi0woYhQtZ3cGia4SjFYWkSKD7dNd2tuSIrAM%0AP2UNW/ySl8kfi40EeW2jr5Xyhmk2sFeulkCkVf5uai9B9W8uCXJqxoNUpOLCRIiv%0AS0W/Ok6FSUw5S1Z6jnGHROjw2kx4JxiZg41uuq8tMn9YP/Vt382c%2Bjd7ygBkaXqK%0ASczokLMKbx8/fvLUbW%2BxN3jrSDXCWfq01gUfORhxYkOgaXAKqVCuzo4gBVfy4mPV%0AUnj/lcnc2bsgBSEqLgqjeDkQIDzXAHlG5725HBLNiem%2Bl/yKY/nhYa4tEM6iJL0A%0Ay%2BAP5XFJuKXBTgz7mXUko9bIrYYH4beUI0ZnaWU2HgW%2Bv1/7buBzEbwfTNQU3HWg%0AK8%2BfHQTElpMLNZGCgZSOtDSzsTy92ymY9DM78T2GKcmm2TFczjqm06/chxdJk0%2BG%0A%2BiiGXt75OlbR%2BUInjCl6WmAdJlWEBD82t%2B4/GAEbswIDAQABo1MwUTAdBgNVHQ4E%0AFgQUXZkjmiCZcdO03Wk3mVb95CXVPR0wHwYDVR0jBBgwFoAUXZkjmiCZcdO03Wk3%0AmVb95CXVPR0wDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAgEAJ5QE%0AU70jacuq5B0C8UZYvLI5JBZwU/xnqOql%2B532Z9pqmAQLNNHzv2dnkoMiSpAZ4HHq%0AbQcbnoYP/zo7L6cQ2Pa%2BKHMN2EmKDkzvxAgh8LRAO%2B2eNzqjs2QT3Dhl0kN/6vRt%0AU7LsLOka2wuXQSbJuf4jffkwJb08PN4CJVT65HFALIOre%2B/EvL0jwlTkGghAanbS%0AH%2B6IT/mwV0t2MsNPvmCNfwKa8ImyqR2SiwgiLveRhtBrb4KvSdT5w8p0tcSdJgT/%0A9OOJYNzsWlNHBdyT8J2pxe9WpwNjZD2VWC6Zcuyn4F%2BrBBMEzY/u55dDIxfe%2BTLH%0AuN/Su2o1YkSOaWdWhJIVXGqG1ZT0IISj8EZ2ZjTZ3iZ8iQ1I384Nxd0uoHoZYCpy%0A/fS5DhnIi5ral8nQCGunjmMMGimHuVdqsu4pL%2BuGsLsbQXZHEXKSlzVQae/GEM4i%0A8zXV3URdCGu64l%2BxIS13yJhi0EY10Lm6f2Rt/FJtRMoJ5UBw1%2B9/ZfEzpk5gwlIs%0AnulBzEFH3H3vNIPngKPtaSgR8UJ529FoXLjduos8dlNU49Ww3RtWFRoixVDxTeez%0AdRAfJou4LcsthIizhfAUAVOfwXuYgwSDe9Rn4Ml/fyPfWAYqz/r146AQvxyBU1wn%0A2iIAx8SQ5hqC0Dh4EB8ooE4StQmIjtlpE%2BCeBEY%3D%0A-----END%20CERTIFICATE-----'
        }
        
    
    def te1st_get_missing_cert(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.data), {'error': 'SSL certificate missing'})

    def te1st_get_invalid_cert(self):
        invalid_headers = {
            'X-SSL-CERT': """-----BEGIN%20CERTIFICATE-----%0AMIIFazC0000000CA1OgAwIBAgIUIHZZhQSazpA9JqPOtHrk9iAPX%2BkwDQYJKoZIhvcNAQEL%0ABQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM%0AGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0yMjExMDIxNTM1MjZaFw0yMzEx%0AMDIxNTM1MjZaMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw%0AHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggIiMA0GCSqGSIb3DQEB%0AAQUAA4ICDwAwggIKAoICAQDNxFhaFSjDxm2GnZ3E7udXtCmG9zA7B%2Bllbta8kdWz%0A8Mwx2CKXR9lejnvKnhEPi3FzyEkdLxpndJqI%2Bdd/GviM6Kn3f2l3l4iFrNW/3vsx%0AOA%2Bc0FkIKF3kUP1G4NZctRjoSRFNPj5c8jzoD7syr6dqKVCyXfkDTnL6u5Ebe0o8%0ATn12SO5I%2B37kg5u9WtHpCBhNtDasTbAkc41uMRgecx31wVj2JMKSWQ48qroRYpxr%0A4YlYXMo%2BgZQ2%2BWQkbpjJBwsKEdMYZWpdtbvQOGEf47CdRjr9NYyzFTBiYsSwvU2B%0AkK4y7TjunQiy8Ml01p8TlVvWOPdla5mJo8KAQ3eua//oKI8SstjzA3HuUJTVN4Ha%0AUBY6D93KcEy4UyWAjXzUTpNjNjOf55UlrXDus9xxzWRTOk9fwVYB0adsorsIXeSw%0ALPefudu94YjP7IXFNf8bqSHC91ILDQeIjymQX7J%2BHTwUZNPv8Wc3p4YbQCXsLeKy%0APdkb3srPrf3tiXgupGUXGOPjDHYCO53UmbXrPMddP20Jv/izysZ%2BDE8fhq9J1rnV%0AqIXDO0MT3KcQbnICBbAkQMh5b7B5Tg3hkFnFNnlnxbPC63RupFTYLmdVaWA%2BWjxM%0AkVEdgyN69taSWt/qpTvE%2B6oxM%2Bq4bkfP63NxCBGRXKXm7G%2BKg2eSruZjgJ5K87P9%0A/QIDAQABo1MwUTAdBgNVHQ4EFgQUDjKLfWtxOGhR8IhTzokb0z%2BCcZowHwYDVR0j%0ABBgwFoAUDjKLfWtxOGhR8IhTzokb0z%2BCcZowDwYDVR0TAQH/BAUwAwEB/zANBgkq%0AhkiG9w0BAQsFAAOCAgEAj32Tzs8HcE/wxAjfGSoJ/cqVRTKk2PeW8qB5LfVYQo82%0AYtxq67RmKnUy4p9DcPy1WDxpFPYjPoQqD01w3RfCTWeJyY9xa/MHLoM%2BqkURX0kl%0AqSGrH8m/%2BNejWu4rDhOXfbQetVbdUhpKe/cGvxMyeLLdKD2ZdcvN0uxdHZ9D5791%0ALWhr335txPyB/PGDCFx2FEE/VIGcDWBD%2BBulC4GQ77LHt8l%2BDCiuDbJ/FhCD%2BR3f%0ASXpNynJ0MyC8zG/Ze7ejutOvxsZALxeSTdpDeBGH8CJY9uvITy6ZdsB3QkZ9DVi8%0A/Cx%2BdXkVPGVBdYs%2BK5LNBHL7QgWAC2quLxt7mFidC%2BGQlij2wMUO%2B2DM1LJOCeEy%0AKZ17FPZiki%2BuEMRMbS8n5GIhsLernoz4IILn5uTj7lr/yd95TJYhM4chXNcfJuZ6%0AuEREZs9v5/KKrCvWPPwoi3wYRE0kxDaBu5Do50kZmT092PloD%2BMi8UphKA7LluhC%0AkiJuID2nPa/JxRFRKBm1netgVRYstuv13REecR7WBQclbuVEo31%2BiED7OWMFdxdn%0Ar2BeIQ6ddhJUiQJdBj2j1/lDqBBNYQsmIZsuVgYwGFb5wA/8C8b8N8ND7XJBAZRj%0A58xvWjhSufBT2fgjYowndLvAzxJ3V%2BGR7LK7BvAKsvaFzducRBrQve6oU7RsHe8%3D%0A-----END%20CERTIFICATE-----"""
        }
        response = self.client.get("/", headers=invalid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.data), {'error': 'SSL certificate could not be parsed'})

    def tes1t_get_missing_cn(self):
        invalid_headers = {
            'X-SSL-CERT': """-----BEGIN%20CERTIFICATE-----%0AMIIFazCCA1OgAwIBAgIUIHZZhQSazpA9JqPOtHrk9iAPX%2BkwDQYJKoZIhvcNAQEL%0ABQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM%0AGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0yMjExMDIxNTM1MjZaFw0yMzEx%0AMDIxNTM1MjZaMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw%0AHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggIiMA0GCSqGSIb3DQEB%0AAQUAA4ICDwAwggIKAoICAQDNxFhaFSjDxm2GnZ3E7udXtCmG9zA7B%2Bllbta8kdWz%0A8Mwx2CKXR9lejnvKnhEPi3FzyEkdLxpndJqI%2Bdd/GviM6Kn3f2l3l4iFrNW/3vsx%0AOA%2Bc0FkIKF3kUP1G4NZctRjoSRFNPj5c8jzoD7syr6dqKVCyXfkDTnL6u5Ebe0o8%0ATn12SO5I%2B37kg5u9WtHpCBhNtDasTbAkc41uMRgecx31wVj2JMKSWQ48qroRYpxr%0A4YlYXMo%2BgZQ2%2BWQkbpjJBwsKEdMYZWpdtbvQOGEf47CdRjr9NYyzFTBiYsSwvU2B%0AkK4y7TjunQiy8Ml01p8TlVvWOPdla5mJo8KAQ3eua//oKI8SstjzA3HuUJTVN4Ha%0AUBY6D93KcEy4UyWAjXzUTpNjNjOf55UlrXDus9xxzWRTOk9fwVYB0adsorsIXeSw%0ALPefudu94YjP7IXFNf8bqSHC91ILDQeIjymQX7J%2BHTwUZNPv8Wc3p4YbQCXsLeKy%0APdkb3srPrf3tiXgupGUXGOPjDHYCO53UmbXrPMddP20Jv/izysZ%2BDE8fhq9J1rnV%0AqIXDO0MT3KcQbnICBbAkQMh5b7B5Tg3hkFnFNnlnxbPC63RupFTYLmdVaWA%2BWjxM%0AkVEdgyN69taSWt/qpTvE%2B6oxM%2Bq4bkfP63NxCBGRXKXm7G%2BKg2eSruZjgJ5K87P9%0A/QIDAQABo1MwUTAdBgNVHQ4EFgQUDjKLfWtxOGhR8IhTzokb0z%2BCcZowHwYDVR0j%0ABBgwFoAUDjKLfWtxOGhR8IhTzokb0z%2BCcZowDwYDVR0TAQH/BAUwAwEB/zANBgkq%0AhkiG9w0BAQsFAAOCAgEAj32Tzs8HcE/wxAjfGSoJ/cqVRTKk2PeW8qB5LfVYQo82%0AYtxq67RmKnUy4p9DcPy1WDxpFPYjPoQqD01w3RfCTWeJyY9xa/MHLoM%2BqkURX0kl%0AqSGrH8m/%2BNejWu4rDhOXfbQetVbdUhpKe/cGvxMyeLLdKD2ZdcvN0uxdHZ9D5791%0ALWhr335txPyB/PGDCFx2FEE/VIGcDWBD%2BBulC4GQ77LHt8l%2BDCiuDbJ/FhCD%2BR3f%0ASXpNynJ0MyC8zG/Ze7ejutOvxsZALxeSTdpDeBGH8CJY9uvITy6ZdsB3QkZ9DVi8%0A/Cx%2BdXkVPGVBdYs%2BK5LNBHL7QgWAC2quLxt7mFidC%2BGQlij2wMUO%2B2DM1LJOCeEy%0AKZ17FPZiki%2BuEMRMbS8n5GIhsLernoz4IILn5uTj7lr/yd95TJYhM4chXNcfJuZ6%0AuEREZs9v5/KKrCvWPPwoi3wYRE0kxDaBu5Do50kZmT092PloD%2BMi8UphKA7LluhC%0AkiJuID2nPa/JxRFRKBm1netgVRYstuv13REecR7WBQclbuVEo31%2BiED7OWMFdxdn%0Ar2BeIQ6ddhJUiQJdBj2j1/lDqBBNYQsmIZsuVgYwGFb5wA/8C8b8N8ND7XJBAZRj%0A58xvWjhSufBT2fgjYowndLvAzxJ3V%2BGR7LK7BvAKsvaFzducRBrQve6oU7RsHe8%3D%0A-----END%20CERTIFICATE-----"""
        }
        response = self.client.get("/", headers=invalid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.data), {'error': 'Missing common name field'})

    def tes1t_missing_request_method(self):
        response = self.client.get("/", headers=self.valid_headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.data), {'error': 'Missing request method header'})

    @mock.patch('server.main.make_ocsp_request', side_effect=mock_bad_ocsp)
    def tes1t_revoked_certificate(self, mock):
        headers = deepcopy(self.valid_headers)
        headers['Request-Method'] = 'GET'
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.data), {'error': 'Certificate is not valid'})

    @mock.patch('server.main.make_ocsp_request', side_effect=mock_good_ocsp)
    @mock.patch('requests.post', side_effect=mocked_requests)
    @mock.patch('requests.get', side_effect=mocked_requests)
    def test_get(self, mock_post, mock_get, mock_ocsp):
        headers = deepcopy(self.valid_headers)
        headers['Request-Method'] = 'GET'
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()