package repository

import "errors"

var (
	ErrAuctionNotFound      = errors.New("auction not found")
	ErrAuctionAlreadyWon    = errors.New("auction already has a winner")
	ErrAuctionAlreadyClosed = errors.New("auction is already closed")
)