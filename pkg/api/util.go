package api

import (
	"crypto/x509"
)

func getTokenCacheKey(userId string) string {
	return "token_" + userId
}

func getOCSPCacheKey(cert x509.Certificate) string {
	return "ocsp_" + cert.SerialNumber.String()
}
