package jwt

import (
    "os"
    "time"
    "errors"
    "fmt"
    "strings"

    "github.com/golang-jwt/jwt/v4"
)

var jwtSecret = []byte(os.Getenv("JWT_SECRET"))

func ExtractBearerToken(authHeader string) (string, error) {
    if !strings.HasPrefix(authHeader, "Bearer ") {
        return "", errors.New("invalid Authorization header")
    }
    return strings.TrimPrefix(authHeader, "Bearer "), nil
}

func ParseToken(tokenStr string) (*jwt.Token, jwt.MapClaims, error) {
    token, err := jwt.Parse(tokenStr, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return jwtSecret, nil
    })
    if err != nil {
        return nil, nil, err
    }

    claims, ok := token.Claims.(jwt.MapClaims)
    if !ok || !token.Valid {
        return nil, nil, errors.New("invalid token claims")
    }

    if exp, ok := claims["exp"].(float64); ok {
        if float64(time.Now().Unix()) > exp {
            return nil, nil, errors.New("token is expired")
        }
    } else {
        return nil, nil, errors.New("missing or invalid 'exp' field")
    }

    return token, claims, nil
}
