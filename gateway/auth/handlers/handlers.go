package handlers

import (
    "encoding/json"
    "log"
    "net/http"
    "strings"

    "github.com/golang-jwt/jwt/v4"
    "github.com/user/forumupd/gateway/auth/db"
    "github.com/user/forumupd/gateway/auth/models"
    "github.com/user/forumupd/gateway/auth/jwt"

)

func CheckPermissionsHandler(w http.ResponseWriter, r *http.Request) {
    authHeader := r.Header.Get("Authorization")
    if authHeader == "" {
        http.Error(w, "Missing Authorization header", http.StatusUnauthorized)
        return
    }

    tokenStr, err := jwt.ExtractBearerToken(authHeader)
    if err != nil {
        http.Error(w, "Invalid Authorization header", http.StatusUnauthorized)
        return
    }

    claims, err := jwt.ParseToken(tokenStr)
    if err != nil {
        log.Println("ParseToken error:", err)
        http.Error(w, "Invalid or expired token", http.StatusUnauthorized)
        return
    }

    userID, ok := claims["sub"].(string)
    if !ok || userID == "" {
        http.Error(w, "Invalid token claims: no user ID", http.StatusBadRequest)
        return
    }

    roles, err := models.GetUserRoles(db.DB, userID)
    if err != nil {
        log.Println("GetUserRoles error:", err)
        http.Error(w, "Failed to get user roles", http.StatusInternalServerError)
        return
    }

    hasStartup := contains(roles, "стартап")
    hasInvestor := contains(roles, "інвестор")

    if !hasStartup && !hasInvestor {
        http.Error(w, "Forbidden", http.StatusForbidden)
        return
    }

    resp := map[string]interface{}{
        "message":  "Access granted",
        "roles":    roles,
        "user_id":  userID,
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
