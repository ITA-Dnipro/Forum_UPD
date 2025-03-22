package main

import (
    "net/http"
    "net/http/httptest"
    "os"
    "strings"
    "testing"
    "time"

    localjwt "github.com/user/forumupd/gateway/auth/jwt"

    "github.com/golang-jwt/jwt/v4"
)

// TestCheckHandler tests the checkHandler function for various scenarios,
// such as missing headers, invalid token formats, role mismatches, and valid tokens.
func TestCheckHandler(t *testing.T) {
	// Set test JWT secret.
    os.Setenv("JWT_SECRET", "testsecret")
    localjwt.SetSecret([]byte("testsecret"))

	// Helper function to create a JWT token.
    createToken := func(role string, exp time.Duration) string {
        claims := jwt.MapClaims{
            "role": role,
            "exp":  time.Now().Add(exp).Unix(),
        }
        token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
        tokenStr, err := token.SignedString([]byte("testsecret"))
        if err != nil {
            t.Fatalf("Error signing token: %v", err)
        }
        return tokenStr
    }

    tests := []struct {
        name           string
        authHeader     string
        requiredRole   string
        expectedStatus int
        expectedBody   string
    }{
        {
            name:           "Missing Authorization header",
            authHeader:     "",
            requiredRole:   "",
            expectedStatus: http.StatusUnauthorized,
            expectedBody:   "Missing Authorization header",
        },
        {
            name:           "Invalid token format",
            authHeader:     "Invalid abc.def.ghi",
            requiredRole:   "",
            expectedStatus: http.StatusUnauthorized,
            expectedBody:   "invalid Authorization header",
        },
        {
            name:           "Valid token, no requiredRole",
            authHeader:     "Bearer " + createToken("IsActive", 1*time.Hour),
            requiredRole:   "",
            expectedStatus: http.StatusOK,
            expectedBody:   "User role: IsActive",
        },
        {
            name:           "Valid token but requiredRole mismatch",
            authHeader:     "Bearer " + createToken("IsActive", 1*time.Hour),
            requiredRole:   "Admin",
            expectedStatus: http.StatusForbidden,
            expectedBody:   "Forbidden for this role",
        },
        {
            name:           "Valid token with matching requiredRole",
            authHeader:     "Bearer " + createToken("Admin", 1*time.Hour),
            requiredRole:   "Admin",
            expectedStatus: http.StatusOK,
            expectedBody:   "User role: Admin",
        },
    }

    for _, tc := range tests {
        t.Run(tc.name, func(t *testing.T) {

            req := httptest.NewRequest("GET", "/check", nil)

            if tc.requiredRole != "" {
                q := req.URL.Query()
                q.Add("requiredRole", tc.requiredRole)
                req.URL.RawQuery = q.Encode()
            }
            req.Header.Set("Authorization", tc.authHeader)
            rr := httptest.NewRecorder()


            checkHandler(rr, req)

            if rr.Code != tc.expectedStatus {
                t.Errorf("Expected status %d, got %d", tc.expectedStatus, rr.Code)
            }
            if !strings.Contains(rr.Body.String(), tc.expectedBody) {
                t.Errorf("Expected body to contain %q, got %q", tc.expectedBody, rr.Body.String())
            }
        })
    }
}
