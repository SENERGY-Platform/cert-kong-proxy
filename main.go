package main

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"fmt"
	log_ "log"
	"net/http"
	"net/http/httputil"
	"net/url"
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
	cacheLib "github.com/SENERGY-Platform/service-commons/pkg/cache"
)

func main() {
	// default configVal
	configVal := config.Config{
		CaUrl:           "http://localhost:8080",
		UpstreamUrl:     "https://api.senergy.infai.org",
		KeycloakUrl:     "https://auth.senergy.infai.org",
		LogHandler:      "text",
		LogLevel:        "debug",
		ServerPort:      8080,
		ServerPortHTTPS: 0,
		CertFile:        "local/ca.crt",
		KeyFile:         "local/ca.key",
	}

	// load config from environment
	if err := envldr.LoadEnv(&configVal); err != nil {
		log_.Fatal(err.Error())
		return
	}

	log.Init(configVal)

	caClient := client.NewClient(configVal.CaUrl)

	cache, err := cacheLib.New(cacheLib.Config{})
	if err != nil {
		log.Logger.Error(fmt.Sprintf("Unable to initialize cache: %v", err))
		return
	}
	upstreamUrl, err := url.Parse(configVal.UpstreamUrl)
	if err != nil {
		log.Logger.Error(fmt.Sprintf("Unable to parse upstream URL: %v", err))
		return
	}
	proxy := &httputil.ReverseProxy{
		Rewrite: func(r *httputil.ProxyRequest) {
			r.SetURL(upstreamUrl)
			r.SetXForwarded()
			// extract token from context and set as Authroization header
			token, ok := r.In.Context().Value(config.TokenContextKey).(string)
			if !ok {
				log.Logger.Error(fmt.Sprintf("Unable to extract token from context: %#v", r.In.Context().Value(config.TokenContextKey)))
			}
			r.Out.Header.Set("Authorization", token)
		},
	}
	ctx, cancel := context.WithCancel(context.Background())
	wg := &sync.WaitGroup{}

	validator := api.NewValidator(caClient, configVal, cache)

	if configVal.ServerPortHTTPS != 0 {
		httpshandler := api.NewHttpsHandler(proxy, validator)

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
		server := &http.Server{Addr: fmt.Sprintf(":%d", configVal.ServerPortHTTPS),
			Handler:   httpshandler,
			TLSConfig: tlsConfig}

		go func() {
			log.Logger.Info("Starting HTTPS server on port " + strconv.FormatUint(uint64(configVal.ServerPortHTTPS), 10))
			err = server.ListenAndServeTLS(configVal.CertFile, configVal.KeyFile)
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
	}
	if configVal.ServerPort != 0 {
		httphandler := api.NewHttpHandler(proxy, validator)

		caCertPool := x509.NewCertPool()
		caCert, code, err := caClient.GetCA(nil)
		if err != nil {
			log.Logger.Error(fmt.Sprintf("Unable to get CA cert: %v (Code %d)", err, code))
			return
		}
		caCertPool.AddCert(caCert)
		server := &http.Server{Addr: fmt.Sprintf(":%d", configVal.ServerPort),
			Handler: httphandler,
		}

		go func() {
			log.Logger.Info("Starting HTTP server on port " + strconv.FormatUint(uint64(configVal.ServerPort), 10))
			err = server.ListenAndServe()
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
	}
	go func() {
		shutdown := make(chan os.Signal, 1)
		signal.Notify(shutdown, syscall.SIGINT, syscall.SIGTERM, syscall.SIGKILL)
		sig := <-shutdown
		log.Logger.Info("received shutdown signal", sig)
		cancel()
	}()

	wg.Wait()
}
