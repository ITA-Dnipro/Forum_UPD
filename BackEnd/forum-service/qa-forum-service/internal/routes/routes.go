package routes

import (
	"github.com/boghtml/qa-forum-service/internal/handlers"
	"github.com/gin-gonic/gin"
)

func SetupRoutes(r *gin.Engine, h *handlers.Handler) {
	api := r.Group("/api/")
	{
		questions := api.Group("/questions")
		{
			questions.GET("/", h.GetQuestions)
			questions.POST("/", h.CreateQuestion)

			question := questions.Group("/:id")
			{
				question.GET("", h.GetQuestion)
				question.PUT("", h.UpdateQuestion)
				question.DELETE("", h.DeleteQuestion)

				question.POST("/save", h.SaveQuestion)
				question.DELETE("/save", h.UnsaveQuestion)
			}
		}

		api.GET("/saved-questions", h.GetSavedQuestions)
	}
}
