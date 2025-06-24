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
}
