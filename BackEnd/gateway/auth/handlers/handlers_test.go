package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	"github.com/golang-jwt/jwt/v4"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	localjwt "github.com/user/forumupd/gateway/auth/jwt"
	db2 "github.com/user/forumupd/gateway/auth/db"
	"github.com/user/forumupd/gateway/auth/models"
)

// createTestToken generates a JWT token for testing purposes
func createTestToken(sub, role string, exp time.Duration) string {
	claims := jwt.MapClaims{
		"sub":  sub,
		"role": role,
		"exp":  time.Now().Add(exp).Unix(),
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenStr, _ := token.SignedString([]byte("testsecret"))
	return tokenStr
}

// TestCheckPermissionsHandler tests the CheckPermissionsHandler function
// using an in-memory SQLite database and a test JWT token.
func TestCheckPermissionsHandler(t *testing.T) {
	// Create an in-memory database for testing.
	testDB, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	if err != nil {
		t.Fatalf("Error opening in-memory database: %v", err)
	}

	// AutoMigrate the models.
	if err := testDB.AutoMigrate(&models.Role{}, &models.Permission{}, &models.RolePermission{}); err != nil {
		t.Fatalf("AutoMigrate failed: %v", err)
	}

	// Seed test data with a role "IsStartup".
	testDB.Create(&models.Role{Model: gorm.Model{ID: 1}, Name: "IsStartup"})

	// Override the global database instance for testing.
	originalDB := db2.DB
	db2.DB = testDB
	defer func() {
		db2.DB = originalDB
	}()

	// Set test JWT secret.
	os.Setenv("JWT_SECRET", "testsecret")
	localjwt.SetSecret([]byte("testsecret"))

	// Create test HTTP request with JWT in header.
	req := httptest.NewRequest("GET", "/permissions", nil)
	tokenStr := createTestToken("user123", "IsActive", 1*time.Hour)
	req.Header.Set("Authorization", "Bearer "+tokenStr)

	rr := httptest.NewRecorder()

	// Call the CheckPermissionsHandler.
	CheckPermissionsHandler(rr, req)

	// Check response status code.
	if rr.Code != http.StatusOK {
		t.Errorf("Expected status 200, got %d", rr.Code)
	}

	// Decode and verify the response body.
	var resp map[string]interface{}
	if err := json.NewDecoder(rr.Body).Decode(&resp); err != nil {
		t.Fatalf("Error decoding JSON: %v", err)
	}

	if resp["message"] != "Access granted" {
		t.Errorf("Expected message 'Access granted', got %v", resp["message"])
	}
	if resp["user_id"] != "user123" {
		t.Errorf("Expected user_id 'user123', got %v", resp["user_id"])
	}
	if resp["isStartup"] != true {
		t.Errorf("Expected isStartup true, got %v", resp["isStartup"])
	}
	if resp["isInvestor"] != false {
		t.Errorf("Expected isInvestor false, got %v", resp["isInvestor"])
	}
}


