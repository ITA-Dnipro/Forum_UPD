package main

import (
	"fmt"
	"github.com/gin-gonic/contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/vladmorozov2/auction-service/internal/handlers"
	"github.com/vladmorozov2/auction-service/internal/models"
	"github.com/vladmorozov2/auction-service/internal/repository"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"log"
	"os"
)

var gormDB *gorm.DB

func main() {
	var err error
	gormDB, err = connectToPostgreSQL()
	if err != nil {
		log.Fatalf("Error connecting to the database: %v", err)
	}
	auctionRepo := repository.NewAuctionRepository(gormDB)
	handler := handlers.NewHandler(auctionRepo)

	router := SetupRoutes(handler)
	router.Run(":8081")
}

func connectToPostgreSQL() (*gorm.DB, error) {
	username := os.Getenv("DB_USER")
	password := os.Getenv("DB_PASSWORD")
	host := os.Getenv("DB_HOST")
	dbname := os.Getenv("DB_NAME")

	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=5432 sslmode=disable",
		host, username, password, dbname)

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, err
	}
	err = db.AutoMigrate(&models.Auction{})
	if err != nil {
		return nil, fmt.Errorf("failed to auto migrate: %v", err)
	}
	err = db.AutoMigrate(&models.Bid{})
	if err != nil {
		return nil, fmt.Errorf("failed to auto migrate: %v", err)
	}


	return db, nil
}

func SetupRoutes(handler *handlers.Handler) *gin.Engine {
	router := gin.Default()

	config := cors.DefaultConfig()
	config.AllowAllOrigins = true
	router.Use(cors.New(config))

	router.POST("/auction", handler.CreateAuction)
	router.GET("/auctions", handler.GetOpenAuctions)
	router.GET("/auction/:id", handler.GetAuctionByID)
	router.POST("/auction/:id/winner", handler.SetAuctionWinner)
	router.GET("/auction/:id/winner", handler.GetAuctionWinnerByID)
	router.POST("/bid/:auction_id", handler.CreateBid)
	router.GET("/bids/:auction_id", handler.GetAllBids)

	return router
}
