package api

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httputil"
	"net/url"
	"time"

	"github.com/SENERGY-Platform/cert-kong-proxy/pkg/log"

	"github.com/SENERGY-Platform/cert-certificate-authority/pkg/client"
	"github.com/SENERGY-Platform/cert-kong-proxy/pkg/config"
	cacheLib "github.com/SENERGY-Platform/service-commons/pkg/cache"
	"github.com/SENERGY-Platform/service-commons/pkg/jwt"
	"golang.org/x/crypto/ocsp"
)

type handler struct {
	caClient client.Client
	config   config.Config
	cache    *cacheLib.Cache
	proxy    http.Handler
}

const tokenContextKey = "token"

func NewHandler(caClient client.Client, config config.Config) (http.Handler, error) {
	cache, err := cacheLib.New(cacheLib.Config{})
	if err != nil {
		return nil, err
	}
	upstreamUrl, err := url.Parse(config.UpstreamUrl)
	if err != nil {
		return nil, err
	}
	proxy := &httputil.ReverseProxy{
		Rewrite: func(r *httputil.ProxyRequest) {
			r.SetURL(upstreamUrl)
			r.SetXForwarded()
			// extract token from context and set as Authroization header
			token, ok := r.In.Context().Value(tokenContextKey).(string)
			if !ok {
				log.Logger.Error(fmt.Sprintf("Unable to extract token from context: %#v", r.In.Context().Value(tokenContextKey)))
			}
			r.Out.Header.Set("Authorization", token)
		},
	}
	return &handler{
		caClient: caClient,
		config:   config,
		cache:    cache,
		proxy:    proxy,
	}, nil
}

func (m *handler) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	// basic checks
	if len(req.TLS.PeerCertificates) == 0 {
		// should be done by Server already, just to be sure
		w.WriteHeader(http.StatusUnauthorized)
		w.Write([]byte("No certificate provided"))
		return
	}
	peerCert := req.TLS.PeerCertificates[0]
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
	ocspResponseValue, err := cacheLib.Get[ocsp.Response](m.cache, ocspCacheKey, cacheLib.NoValidation)
	if err == nil {
		// cache found
		log.Logger.Debug(fmt.Sprintf("Using cached OCSP Response for user %s", userId))
		ocspResponse = &ocspResponseValue
	} else {
		// cache miss
		log.Logger.Debug(fmt.Sprintf("Getting new OCSP Response for user %s", userId))
		_, ocspResponse, _, err = m.caClient.GetStatus(peerCert, nil)
		if err != nil {
			w.WriteHeader(http.StatusBadGateway)
			w.Write([]byte("Unable to verify certificate at CA"))
			return
		}
		err = m.cache.Set(ocspCacheKey, *ocspResponse, time.Minute)
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
	token, err = cacheLib.Get[jwt.Token](m.cache, tokenCacheKey, cacheLib.NoValidation)
	if err != nil {
		// cache miss
		log.Logger.Debug(fmt.Sprintf("Getting new token for user %s", userId))
		var expiration time.Duration
		token, expiration, err = jwt.ExchangeUserToken(m.config.KeycloakUrl, m.config.KeycloakClientId, m.config.KeycloakClientSecret, userId)
		if err != nil {
			w.WriteHeader(http.StatusBadGateway)
			w.Write([]byte("Unable to get user token"))
			return
		}
		err = m.cache.Set(tokenCacheKey, token, expiration)
		if err != nil {
			log.Logger.Warn(fmt.Sprintf("Unable to write to cache: %v", err))
		}
	} else {
		log.Logger.Debug(fmt.Sprintf("Using cached token of user %s", userId))
	}
	// set token in context
	// the reverse proxy extracts the token from the context and sets it as header
	req = req.WithContext(context.WithValue(req.Context(), tokenContextKey, token.Token))
	m.proxy.ServeHTTP(w, req)
}
