package repository

import (
	"github.com/vladmorozov2/auction-service/internal/models"
	"gorm.io/gorm"
	// "time"
	"context"
)

type Repository interface {
	CreateAuction(ctx context.Context, auction *models.Auction) error
	GetOpenAuctions(ctx context.Context) ([]*models.Auction, error)
	GetAuctionByID(ctx context.Context, id string) (*models.Auction, error)
	SetAuctionWinner(ctx context.Context, auctionID string, winnerID int) error
	CreateBid(ctx context.Context, bid *models.Bid) error
	GetLastBidForAuction(ctx context.Context, auctionID string) (*models.Bid, error)
	GetBidsByAuctionID(ctx context.Context, auctionID string) ([]*models.Bid, error)
}

type PostgreSQL struct {
	db *gorm.DB
}

func NewAuctionRepository(db *gorm.DB) Repository {
	return &PostgreSQL{db: db}
}
