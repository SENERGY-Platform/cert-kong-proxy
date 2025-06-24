package api

import (
	"context"
	"crypto/x509"
	"fmt"
	"net/http"
	"time"

	"github.com/SENERGY-Platform/cert-kong-proxy/pkg/log"

	"github.com/SENERGY-Platform/cert-certificate-authority/pkg/client"
	"github.com/SENERGY-Platform/cert-kong-proxy/pkg/config"
	cacheLib "github.com/SENERGY-Platform/service-commons/pkg/cache"
	"github.com/SENERGY-Platform/service-commons/pkg/jwt"
	"golang.org/x/crypto/ocsp"
)

type Validator struct {
	caClient client.Client
	config   config.Config
	cache    *cacheLib.Cache
}

func NewValidator(caClient client.Client, config config.Config, cache *cacheLib.Cache) *Validator {
	return &Validator{
		caClient: caClient,
		config:   config,
		cache:    cache,
	}
}

func (v *Validator) validate(peerCert *x509.Certificate, w http.ResponseWriter, req *http.Request) (cont bool) {
	expired := peerCert.NotAfter.Before(time.Now())
	if expired {
		// should be done by Server already, just to be sure
		w.WriteHeader(http.StatusUnauthorized)
		w.Write([]byte("Certificate expired"))
		return
	}
	userId := peerCert.Subject.CommonName

	// check ocsp
	ocspCacheKey := getOCSPCacheKey(*peerCert)
	var ocspResponse *ocsp.Response
	ocspResponseValue, err := cacheLib.Get[ocsp.Response](v.cache, ocspCacheKey, cacheLib.NoValidation)
	if err == nil {
		// cache found
		log.Logger.Debug(fmt.Sprintf("Using cached OCSP Response for user %s", userId))
		ocspResponse = &ocspResponseValue
	} else {
		// cache miss
		log.Logger.Debug(fmt.Sprintf("Getting new OCSP Response for user %s", userId))
		_, ocspResponse, _, err = v.caClient.GetStatus(peerCert, nil)
		if err != nil {
			w.WriteHeader(http.StatusBadGateway)
			w.Write([]byte("Unable to verify certificate at CA"))
			return
		}
		err = v.cache.Set(ocspCacheKey, *ocspResponse, time.Minute)
		if err != nil {
			log.Logger.Warn(fmt.Sprintf("Unable to write to cache: %v", err))
		}
	}
	if ocspResponse.Status != ocsp.Good {
		w.WriteHeader(http.StatusUnauthorized)
		w.Write([]byte("Certificate OCSP status not good"))
		return
	}

	// get token
	tokenCacheKey := getTokenCacheKey(userId)
	var token jwt.Token
	token, err = cacheLib.Get[jwt.Token](v.cache, tokenCacheKey, cacheLib.NoValidation)
	if err != nil {
		// cache miss
		log.Logger.Debug(fmt.Sprintf("Getting new token for user %s", userId))
		var expiration time.Duration
		token, expiration, err = jwt.ExchangeUserToken(v.config.KeycloakUrl, v.config.KeycloakClientId, v.config.KeycloakClientSecret, userId)
		if err != nil {
			w.WriteHeader(http.StatusBadGateway)
			w.Write([]byte("Unable to get user token"))
			return
		}
		err = v.cache.Set(tokenCacheKey, token, expiration)
		if err != nil {
			log.Logger.Warn(fmt.Sprintf("Unable to write to cache: %v", err))
		}
	} else {
		log.Logger.Debug(fmt.Sprintf("Using cached token of user %s", userId))
	}
	*req = *req.WithContext(context.WithValue(req.Context(), config.TokenContextKey, token.Token))
	return true
}
