package jwt

import (
	"os"
	"testing"
	"time"

	"github.com/golang-jwt/jwt/v4"
)

// initTest sets up the JWT secret for testing purposes.
func init() {
	os.Setenv("JWT_SECRET", "testsecret")
	jwtSecret = []byte("testsecret")
}

// TestExtractBearerToken verifies that ExtractBearerToken correctly extracts
// the token from a valid Authorization header and returns an error for invalid formats.
func TestExtractBearerToken(t *testing.T) {
	validHeader := "Bearer abc.def.ghi"
	token, err := ExtractBearerToken(validHeader)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if token != "abc.def.ghi" {
		t.Errorf("Expected token 'abc.def.ghi', got %s", token)
	}

	invalidHeader := "Token abc.def.ghi"
	_, err = ExtractBearerToken(invalidHeader)
	if err == nil {
		t.Error("Expected error for invalid header format, got nil")
	}
}

// TestParseToken verifies that ParseToken correctly parses a valid token,
// detects expired tokens, and handles tokens missing the "exp" field.
func TestParseToken(t *testing.T) {
	// Create a valid token.
	claims := jwt.MapClaims{
		"role": "IsActive",
		"exp":  time.Now().Add(1 * time.Hour).Unix(),
		"sub":  "12345",
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenStr, err := token.SignedString(jwtSecret)
	if err != nil {
		t.Fatalf("Error signing token: %v", err)
	}

	parsedToken, parsedClaims, err := ParseToken(tokenStr)
	if err != nil || !parsedToken.Valid {
		t.Errorf("Expected valid token, got error: %v", err)
	}
	if parsedClaims["role"] != "IsActive" {
		t.Errorf("Expected role 'IsActive', got %v", parsedClaims["role"])
	}

	// Test expired token.
	claims["exp"] = time.Now().Add(-1 * time.Hour).Unix()
	tokenExpired := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenExpiredStr, _ := tokenExpired.SignedString(jwtSecret)
	_, _, err = ParseToken(tokenExpiredStr)
	if err == nil {
		t.Error("Expected error for expired token, got nil")
	}

	// Test token missing exp field.
	delete(claims, "exp")
	tokenNoExp := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenNoExpStr, _ := tokenNoExp.SignedString(jwtSecret)
	_, _, err = ParseToken(tokenNoExpStr)
	if err == nil {
		t.Error("Expected error for token missing exp field, got nil")
	}
}
