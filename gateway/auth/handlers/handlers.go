package handlers

import (
    "encoding/json"
    "log"
    "net/http"
    "strings"

    jwt "github.com/golang-jwt/jwt/v4"
    "github.com/user/forumupd/gateway/auth/db"
    "github.com/user/forumupd/gateway/auth/models"
    authjwt "github.com/user/forumupd/gateway/auth/jwt"

)

func CheckPermissionsHandler(w http.ResponseWriter, r *http.Request) {
    authHeader := r.Header.Get("Authorization")
    if authHeader == "" {
        http.Error(w, "Missing Authorization header", http.StatusUnauthorized)
        return
    }

    tokenStr, err := authjwt.ExtractBearerToken(authHeader)
    if err != nil {
        http.Error(w, "Invalid Authorization header", http.StatusUnauthorized)
        return
    }

    token, err := authjwt.ParseToken(tokenStr)
    if err != nil {
        log.Println("ParseToken error:", err)
        http.Error(w, "Invalid or expired token", http.StatusUnauthorized)
        return
    }

    claims, ok := token.Claims.(jwt.MapClaims)
    if !ok {
        http.Error(w, "Invalid token claims", http.StatusUnauthorized)
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
            http.Error(w, "User not found", http.StatusNotFound)
        } else {
            log.Println("Database error fetching roles:", err)
            http.Error(w, "Database error", http.StatusInternalServerError)
        }
        return
    }

    hasStartup := contains(roles, "IsStartup")
    hasInvestor := contains(roles, "IsInvestor")

    if !hasStartup && !hasInvestor {
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

func contains(slice []string, val string) bool {
    for _, item := range slice {
        if strings.EqualFold(item, val) {
            return true
        }
    }
    return false
}
