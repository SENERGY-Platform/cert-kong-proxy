/*
 * Copyright 2025 InfAI (CC SES)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package api

import (
	"crypto/x509"
	"encoding/pem"
	"net/http"
	"net/url"
)

type httpHandler struct {
	proxy     http.Handler
	validator *Validator
}

func NewHttpHandler(proxy http.Handler, validator *Validator) http.Handler {
	return &httpHandler{
		proxy:     proxy,
		validator: validator,
	}
}

func (h *httpHandler) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	// basic checks
	pemStrUrlEnc := req.Header.Get("X-SSL-CERT")
	if len(pemStrUrlEnc) == 0 {
		// should be done by Server already, just to be sure
		w.WriteHeader(http.StatusUnauthorized)
		w.Write([]byte("No certificate provided"))
		return
	}
	pemStr, err := url.QueryUnescape(pemStrUrlEnc)
	if len(pemStrUrlEnc) == 0 {
		w.WriteHeader(http.StatusUnauthorized)
		w.Write([]byte("Unable to decode certificate provided"))
		return
	}
	block, _ := pem.Decode([]byte(pemStr))
	cert, err := x509.ParseCertificate(block.Bytes)
	if err != nil {
		w.WriteHeader(http.StatusUnauthorized)
		w.Write([]byte("Unable to parse certificate provided"))
	}
	if h.validator.validate(cert, w, req) {
		h.proxy.ServeHTTP(w, req)
	}
}
