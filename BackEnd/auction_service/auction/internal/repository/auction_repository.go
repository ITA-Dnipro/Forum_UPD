package repository

import (
	"context"
	"errors"
	"github.com/google/uuid"
	"github.com/vladmorozov2/auction-service/internal/models"
	"gorm.io/gorm"
	"time"
)

func (p *PostgreSQL) CreateAuction(ctx context.Context, auction *models.Auction) error {
	auction.UpdatedAt = time.Now()
	auction.CreatedAt = time.Now()
	auction.ID = uuid.New()
	if auction.Status == "" {
		auction.Status = "open"
	}


	return p.db.WithContext(ctx).Create(auction).Error
}

func (p *PostgreSQL) GetOpenAuctions(ctx context.Context) ([]*models.Auction, error) {
	var auctions []*models.Auction
	err := p.db.WithContext(ctx).Where("status = ?", "open").Find(&auctions).Error
	if err != nil {
		return nil, err
	}
	return auctions, nil
}

func (p *PostgreSQL) GetAuctionByID(ctx context.Context, id string) (*models.Auction, error) {
	var auction models.Auction
	err := p.db.WithContext(ctx).Where("id = ?", id).First(&auction).Error
	if err != nil {
		return nil, err
	}
	return &auction, nil
}
func (p *PostgreSQL) SetAuctionWinner(ctx context.Context, auctionID string, winnerID int) error {
	return p.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		// Fetch the auction to check its current state
		var auction models.Auction
		if err := tx.Where("id = ?", auctionID).First(&auction).Error; err != nil {
			if errors.Is(err, gorm.ErrRecordNotFound) {
				return ErrAuctionNotFound
			}
			return err
		}

		// Check if winner_id is already set (nil means "none")
		if auction.WinnerID != nil {
			return ErrAuctionAlreadyWon
		}

		// Check if the auction is already closed
		if auction.Status == "closed" {
			return ErrAuctionAlreadyClosed
		}

		// Update winner_id and status to "closed"
		updates := map[string]interface{}{
			"winner_id": winnerID,
			"status":    "closed",
		}
		if err := tx.Model(&auction).Updates(updates).Error; err != nil {
			return err
		}

		return nil
	})
}
