package api

import (
	"net/http"
)

type httpsHandler struct {
	proxy     http.Handler
	validator *Validator
}

func NewHttpsHandler(proxy http.Handler, validator *Validator) http.Handler {
	return &httpsHandler{
		proxy:     proxy,
		validator: validator,
	}
}

func (h *httpsHandler) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	// basic checks
	if len(req.TLS.PeerCertificates) == 0 {
		// should be done by Server already, just to be sure
		w.WriteHeader(http.StatusUnauthorized)
		w.Write([]byte("No certificate provided"))
		return
	}
	if h.validator.validate(req.TLS.PeerCertificates[0], w, req) {
		h.proxy.ServeHTTP(w, req)
	}
}
