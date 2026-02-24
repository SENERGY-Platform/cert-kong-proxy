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
	"net/http"

	"github.com/SENERGY-Platform/cert-kong-proxy/pkg/log"
	"github.com/SENERGY-Platform/service-commons/pkg/accesslog"
)

type httpsHandler struct {
	proxy     http.Handler
	validator *Validator
}

func NewHttpsHandler(proxy http.Handler, validator *Validator) http.Handler {
	return accesslog.NewWithLogger(&httpHandler{
		proxy:     proxy,
		validator: validator,
	}, log.Logger)
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
