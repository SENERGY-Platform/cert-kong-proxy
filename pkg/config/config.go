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

package config

type Config struct {
	CaUrl                string `env_var:"CA_URL"`
	CertFile             string `env_var:"CERT_FILE"`
	KeyFile              string `env_var:"KEY_FILE"`
	UpstreamUrl          string `env_var:"UPSTREAM_URL"`
	KeycloakUrl          string `env_var:"KEYCLOAK_URL"`
	KeycloakClientId     string `env_var:"KEYCLOAK_CLIENT_ID"`
	KeycloakClientSecret string `env_var:"KEYCLOAK_CLIENT_SECRET"`
	LogLevel             string `env_var:"LOG_LEVEL"`
	LogHandler           string `env_var:"LOG_HANDLER"`
	ServerPort           uint   `env_var:"SERVER_PORT"`
	ServerPortHTTPS      uint   `env_var:"SERVER_PORT_HTTPS"`
}

const TokenContextKey = "token"
