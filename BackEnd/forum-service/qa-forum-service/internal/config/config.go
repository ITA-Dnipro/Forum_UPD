package config

import (
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	ServerPort string
	ScyllaDB   ScyllaDBConfig
}

type ScyllaDBConfig struct {
	Hosts    string
	Keyspace string
	Username string
	Password string
}

func LoadConfig() (*Config, error) {
	if err := godotenv.Load(); err != nil {
		return nil, err
	}

	return &Config{
		ServerPort: os.Getenv("SERVER_PORT"),
		ScyllaDB: ScyllaDBConfig{
			Hosts:    os.Getenv("SCYLLA_HOSTS"),
			Keyspace: os.Getenv("SCYLLA_KEYSPACE"),
			Username: os.Getenv("SCYLLA_USERNAME"),
			Password: os.Getenv("SCYLLA_PASSWORD"),
		},
	}, nil
}
