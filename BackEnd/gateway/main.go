package main

import (
	"io/ioutil"
	"net/http"
	"time"
)

// AuthMiddleware – це функція, що приймає наступний обробник і повертає новий,
// який спочатку виконує перевірку JWT токена.
func AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Отримання токена з заголовку Authorization
		token := r.Header.Get("Authorization")
		if token == "" {
			http.Error(w, "Unauthorized: missing token", http.StatusUnauthorized)
			return
		}

		// Виклик ендпоінта /validate авторизаційного сервісу
		client := &http.Client{Timeout: 5 * time.Second}
		req, err := http.NewRequest("GET", "http://authentication_service/validate", nil)
		if err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
		req.Header.Set("Authorization", token)

		resp, err := client.Do(req)
		if err != nil || resp.StatusCode != http.StatusOK {
			http.Error(w, "Unauthorized: token validation failed", http.StatusUnauthorized)
			return
		}
		// Опціонально: можна зчитати відповідь для вилучення ролі користувача
		_, err = ioutil.ReadAll(resp.Body)
		resp.Body.Close()
		if err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}

		// Якщо валідація успішна – передаємо запит далі
		next.ServeHTTP(w, r)
	})
}
