package log

import (
	"log/slog"
	"os"

	"github.com/SENERGY-Platform/cert-kong-proxy/pkg/config"
	slogger "github.com/SENERGY-Platform/go-service-base/struct-logger"
	"github.com/SENERGY-Platform/go-service-base/struct-logger/attributes"
)

var Logger *slog.Logger

func Init(config config.Config) {
	options := &slog.HandlerOptions{
		AddSource: false,
		Level:     slogger.GetLevel(config.LogLevel, slog.LevelWarn),
	}

	handler := slogger.GetHandler(config.LogHandler, os.Stdout, options, slog.Default().Handler())
	handler = handler.WithAttrs([]slog.Attr{
		slog.String(attributes.ProjectKey, "github.com/SENERGY-Platform/cert-kong-proxy"),
	})

	Logger = slog.New(handler)

	Logger.Debug("Logger Init")
}
