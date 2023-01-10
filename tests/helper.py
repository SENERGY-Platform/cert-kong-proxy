import json 

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.content = json.dumps(json_data)
            
    def json(self):
        return self.json_data

def get_valid_token(*args, **kwargs):
    return MockResponse({"access_token": "token"}, 200)

def get_invalid_token(*args, **kwargs):
    return MockResponse({}, 200)

def forward_request(*args, **kwargs):
    return MockResponse({"key2": "value2"}, 200)

def get_revoked_ocsp(*args, **kwargs):
    return MockResponse({"success": True, "result": {"ocspResponse": "MIIBpgoBAKCCAZ8wggGbBgkrBgEFBQcwAQEEggGMMIIBiDCCAS2hgY0wgYoxCzAJBgNVBAYTAkdCMRAwDgYDVQQIEwdFbmdsYW5kMQ8wDQYDVQQHEwZMb25kb24xFzAVBgNVBAoTDkN1c3RvbSBXaWRnZXRzMR0wGwYDVQQLExRDdXN0b20gV2lkZ2V0cyBIb3N0czEgMB4GA1UEAxMXaG9zdC5jdXN0b20td2lkZ2V0cy5jb20YDzIwMjIxMTA3MTYxMjAwWjCBiTCBhjBNMAkGBSsOAwIaBQAEFPrV+RrWDPtgcbhxno6XvaaV361kBBTn+cMADvAY8MArXNbSGJHbm7hFiAIUPesGbRICmm6SRHdDZF+tVCw8UE6hERgPMjAyMjExMDcxNjEyNTdaGA8yMDIyMTEwNzE2MDAwMFqgERgPMjAyMjExMDcxNjAwMDBaMAoGCCqGSM49BAMCA0kAMEYCIQCXA/4MhEytd3e89KwOygJa85SXAZRH5uF7yl0bsWIfvAIhAK3F8vobTHfh4c4bAu59F1Am2A70D5NYo6PF2/7fAz6w"}}, 200)

def get_good_ocsp(*args, **kwargs):
    return MockResponse({"success": True, "result": {"ocspResponse": "MIIBkgoBAKCCAYswggGHBgkrBgEFBQcwAQEEggF4MIIBdDCCARqhgY0wgYoxCzAJBgNVBAYTAkdCMRAwDgYDVQQIEwdFbmdsYW5kMQ8wDQYDVQQHEwZMb25kb24xFzAVBgNVBAoTDkN1c3RvbSBXaWRnZXRzMR0wGwYDVQQLExRDdXN0b20gV2lkZ2V0cyBIb3N0czEgMB4GA1UEAxMXaG9zdC5jdXN0b20td2lkZ2V0cy5jb20YDzIwMjIxMTA3MTQ1OTAwWjB3MHUwTTAJBgUrDgMCGgUABBT61fka1gz7YHG4cZ6Ol72mld+tZAQU5/nDAA7wGPDAK1zW0hiR25u4RYgCFCfFxWhLdjmXN51pWcBDRYPl82/XgAAYDzIwMjIxMTA3MTQwMDAwWqARGA8yMDIyMTEwNzE0MDAwMFowCgYIKoZIzj0EAwIDSAAwRQIhAJi2F84DmS/TxLwikTH9LM/vzKipvPLipWFRtatsM+VsAiBVk0hxd0ENHKyP5IbXd3Fc/ifIRW6NU8AnikoQmNJPiw=="}}, 200)

def get_error_ocsp(*args, **kwargs):
    return MockResponse({"success": False, "errors": "error"}, 200)

def get_invalid_ocsp_response(*args, **kwargs):
    return MockResponse({"success": True, "result": {"ocspResponse": "bla"}}, 500)

VALID_CERT = '-----BEGIN%20CERTIFICATE-----%0AMIIFiTCCA3GgAwIBAgIUAlplxT/x5EsyVV8%2BR/Dz9aqRQpYwDQYJKoZIhvcNAQEL%0ABQAwVDELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM%0AGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDENMAsGA1UEAwwEdXNlcjAeFw0yMjEx%0AMDMxMTA5NTZaFw0yMzExMDMxMTA5NTZaMFQxCzAJBgNVBAYTAkFVMRMwEQYDVQQI%0ADApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQx%0ADTALBgNVBAMMBHVzZXIwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQC1%0A6StfmZUfskoLxLIfO18tSJ7nO%2B0fGlnevVi58nohyHEeG0XH7K3GALipP43WOCHZ%0A91a17783Anea/YD0gtrbgjCoLjTcxGdRMFCQcSG3YsB95DKz4%2BFtu9%2BqxQloaQ82%0AknkjDugyXSPJcLDauyNklRR5tsJv6MroBO1uJYaLCHFPBdV9UxBOTnikcpLZzTBu%0Ab4UxJAJta4DZrhlQNij2/HL%2BGbcJi0woYhQtZ3cGia4SjFYWkSKD7dNd2tuSIrAM%0AP2UNW/ySl8kfi40EeW2jr5Xyhmk2sFeulkCkVf5uai9B9W8uCXJqxoNUpOLCRIiv%0AS0W/Ok6FSUw5S1Z6jnGHROjw2kx4JxiZg41uuq8tMn9YP/Vt382c%2Bjd7ygBkaXqK%0ASczokLMKbx8/fvLUbW%2BxN3jrSDXCWfq01gUfORhxYkOgaXAKqVCuzo4gBVfy4mPV%0AUnj/lcnc2bsgBSEqLgqjeDkQIDzXAHlG5725HBLNiem%2Bl/yKY/nhYa4tEM6iJL0A%0Ay%2BAP5XFJuKXBTgz7mXUko9bIrYYH4beUI0ZnaWU2HgW%2Bv1/7buBzEbwfTNQU3HWg%0AK8%2BfHQTElpMLNZGCgZSOtDSzsTy92ymY9DM78T2GKcmm2TFczjqm06/chxdJk0%2BG%0A%2BiiGXt75OlbR%2BUInjCl6WmAdJlWEBD82t%2B4/GAEbswIDAQABo1MwUTAdBgNVHQ4E%0AFgQUXZkjmiCZcdO03Wk3mVb95CXVPR0wHwYDVR0jBBgwFoAUXZkjmiCZcdO03Wk3%0AmVb95CXVPR0wDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAgEAJ5QE%0AU70jacuq5B0C8UZYvLI5JBZwU/xnqOql%2B532Z9pqmAQLNNHzv2dnkoMiSpAZ4HHq%0AbQcbnoYP/zo7L6cQ2Pa%2BKHMN2EmKDkzvxAgh8LRAO%2B2eNzqjs2QT3Dhl0kN/6vRt%0AU7LsLOka2wuXQSbJuf4jffkwJb08PN4CJVT65HFALIOre%2B/EvL0jwlTkGghAanbS%0AH%2B6IT/mwV0t2MsNPvmCNfwKa8ImyqR2SiwgiLveRhtBrb4KvSdT5w8p0tcSdJgT/%0A9OOJYNzsWlNHBdyT8J2pxe9WpwNjZD2VWC6Zcuyn4F%2BrBBMEzY/u55dDIxfe%2BTLH%0AuN/Su2o1YkSOaWdWhJIVXGqG1ZT0IISj8EZ2ZjTZ3iZ8iQ1I384Nxd0uoHoZYCpy%0A/fS5DhnIi5ral8nQCGunjmMMGimHuVdqsu4pL%2BuGsLsbQXZHEXKSlzVQae/GEM4i%0A8zXV3URdCGu64l%2BxIS13yJhi0EY10Lm6f2Rt/FJtRMoJ5UBw1%2B9/ZfEzpk5gwlIs%0AnulBzEFH3H3vNIPngKPtaSgR8UJ529FoXLjduos8dlNU49Ww3RtWFRoixVDxTeez%0AdRAfJou4LcsthIizhfAUAVOfwXuYgwSDe9Rn4Ml/fyPfWAYqz/r146AQvxyBU1wn%0A2iIAx8SQ5hqC0Dh4EB8ooE4StQmIjtlpE%2BCeBEY%3D%0A-----END%20CERTIFICATE-----'
