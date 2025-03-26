package handlers

import (
    "encoding/json"
    "log"
    "net/http"
    "strings"

//     jwt "github.com/golang-jwt/jwt/v4"
    "gorm.io/gorm"

    "github.com/user/forumupd/gateway/auth/db"
    "github.com/user/forumupd/gateway/auth/models"
    localjwt "github.com/user/forumupd/gateway/auth/jwt"

)

// CheckPermissionsHandler validates the JWT token and user permissions.
// It extracts the token from the Authorization header, parses it,
// retrieves the user roles from the database, and verifies if the user
// has either "IsStartup" or "IsInvestor" role. A successful check returns
// an HTTP 200 with a JSON response; otherwise, it returns an appropriate error.
func CheckPermissionsHandler(w http.ResponseWriter, r *http.Request) {
    authHeader := r.Header.Get("Authorization")
    if authHeader == "" {
    	log.Println("Missing Authorization header")
        http.Error(w, "Missing Authorization header", http.StatusUnauthorized)
        return
    }

    tokenStr, err := localjwt.ExtractBearerToken(authHeader)
    if err != nil {
    	log.Printf("Error extracting token: %v", err)
        http.Error(w, "Invalid Authorization header", http.StatusUnauthorized)
        return
    }

    _, claims, err := localjwt.ParseToken(tokenStr)
    if err != nil {
		log.Printf("ParseToken error: %v", err)
        http.Error(w, "Invalid or expired token", http.StatusUnauthorized)
        return
    }

    userID, ok := claims["sub"].(string)
    if !ok {
		log.Println("Invalid token claims: 'sub' is missing or not a string")
        http.Error(w, "Invalid token claims", http.StatusBadRequest)
        return
    }

    roles, err := models.GetUserRoles(db.DB, userID)
    if err != nil {
        if err == gorm.ErrRecordNotFound {
        	log.Printf("User %s not found", userID)
            http.Error(w, "User not found", http.StatusNotFound)
        } else {
			log.Printf("Database error fetching roles for user %s: %v", userID, err)
            http.Error(w, "Database error", http.StatusInternalServerError)
        }
        return
    }

    hasStartup := contains(roles, "IsStartup")
    hasInvestor := contains(roles, "IsInvestor")

    if !hasStartup && !hasInvestor {
    	log.Printf("User %s does not have required permissions", userID)
        http.Error(w, "Forbidden", http.StatusForbidden)
        return
    }

    resp := map[string]interface{}{
        "message":    "Access granted",
        "roles":      roles,
        "user_id":    userID,
        "isStartup":  hasStartup,
        "isInvestor": hasInvestor,
    }
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(resp)
}

// contains checks if the slice contains the given value (case-insensitive).
func contains(slice []string, val string) bool {
    for _, item := range slice {
        if strings.EqualFold(item, val) {
            return true
        }
    }
    return false
}
