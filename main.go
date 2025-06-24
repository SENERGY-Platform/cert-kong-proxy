package main

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"fmt"
	log_ "log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"sync"
	"syscall"
	"time"

	"github.com/SENERGY-Platform/cert-kong-proxy/pkg/log"
	envldr "github.com/SENERGY-Platform/go-env-loader"

	"github.com/SENERGY-Platform/cert-certificate-authority/pkg/client"
	"github.com/SENERGY-Platform/cert-kong-proxy/pkg/api"
	"github.com/SENERGY-Platform/cert-kong-proxy/pkg/config"
)

func main() {
	// default config
	config := config.Config{
		CaUrl:       "http://localhost:8080",
		UpstreamUrl: "https://api.senergy.infai.org",
		KeycloakUrl: "https://auth.senergy.infai.org",
		LogHandler:  "text",
		LogLevel:    "debug",
		ServerPort:  8084,
		CertFile:    "local/ca.crt",
		KeyFile:     "local/ca.key",
	}

	// load config from environment
	if err := envldr.LoadEnv(&config); err != nil {
		log_.Fatal(err.Error())
		return
	}

	log.Init(config)

	caClient := client.NewClient(config.CaUrl)

	caCertPool := x509.NewCertPool()
	caCert, code, err := caClient.GetCA(nil)
	if err != nil {
		log.Logger.Error(fmt.Sprintf("Unable to get CA cert: %v (Code %d)", err, code))
		return
	}
	caCertPool.AddCert(caCert)

	tlsConfig := &tls.Config{
		ClientCAs:  caCertPool,
		ClientAuth: tls.RequireAndVerifyClientCert,
		MinVersion: tls.VersionTLS12,
	}

	handler, err := api.NewHandler(caClient, config)
	if err != nil {
		log.Logger.Error(fmt.Sprintf("Unable to initialize handler: %v", err))
		return
	}

	ctx, cancel := context.WithCancel(context.Background())
	wg := &sync.WaitGroup{}

	server := &http.Server{Addr: fmt.Sprintf(":%d", config.ServerPort),
		Handler:   handler,
		TLSConfig: tlsConfig}

	go func() {
		log.Logger.Info("Starting server on port " + strconv.FormatUint(uint64(config.ServerPort), 10))
		err = server.ListenAndServeTLS(config.CertFile, config.KeyFile)
		if err != nil {
			log.Logger.Error(err.Error())
			cancel()
		}
	}()

	wg.Add(1)
	go func() {
		<-ctx.Done()
		shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 3*time.Second)
		defer shutdownCancel()
		err = server.Shutdown(shutdownCtx)
		if err != nil {
			log.Logger.Error(err.Error())
		}
		wg.Done()
	}()
	go func() {
		shutdown := make(chan os.Signal, 1)
		signal.Notify(shutdown, syscall.SIGINT, syscall.SIGTERM, syscall.SIGKILL)
		sig := <-shutdown
		log.Logger.Info("received shutdown signal", sig)
		cancel()
	}()

	wg.Wait()
}
