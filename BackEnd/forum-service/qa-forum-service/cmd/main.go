package main

import (
	"log"
	"time"

	"github.com/boghtml/qa-forum-service/internal/config"
	"github.com/boghtml/qa-forum-service/internal/handlers"
	"github.com/boghtml/qa-forum-service/internal/migrations"
	"github.com/boghtml/qa-forum-service/internal/repository"
	"github.com/boghtml/qa-forum-service/internal/routes"
	"github.com/gin-gonic/gin"
)

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	time.Sleep(time.Second * 5)

	initialDB, err := repository.NewScyllaDB(cfg.ScyllaDB.Hosts, "system")
	if err != nil {
		log.Fatalf("Failed to connect to ScyllaDB: %v", err)
	}

	err = migrations.CreateKeyspace(initialDB.GetSession(), cfg.ScyllaDB.Keyspace)
	if err != nil {
		log.Fatalf("Failed to create keyspace: %v", err)
	}
	initialDB.Close()

	db, err := repository.NewScyllaDB(cfg.ScyllaDB.Hosts, cfg.ScyllaDB.Keyspace)
	if err != nil {
		log.Fatalf("Failed to connect to ScyllaDB: %v", err)
	}
	defer db.Close()

	err = migrations.RunMigrations(db.GetSession(), "internal/migrations")
	if err != nil {
		log.Fatalf("Failed to run migrations: %v", err)
	}

	h := handlers.NewHandler(db)

	r := gin.Default()
	routes.SetupRoutes(r, h)

	if err := r.Run(":" + cfg.ServerPort); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
