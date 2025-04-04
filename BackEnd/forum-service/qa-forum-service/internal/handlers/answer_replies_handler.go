package handlers

import (
	"fmt"
	"log"
	"net/http"

	"github.com/boghtml/qa-forum-service/internal/models"
	"github.com/gin-gonic/gin"
	"github.com/gocql/gocql"
)

// @Summary Create a reply to an answer
// @Description Creates a new reply to a specific answer within a question
// @Tags Replies
// @Accept json
// @Produce json
// @Param id path string true "Question ID"
// @Param answerId path string true "Answer ID"
// @Param reply body models.AnswerReply true "Reply data"
// @Success 201 {object} models.AnswerReply "Created reply"
// @Failure 400 {object} map[string]string "Invalid question ID, answer ID, or request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/answers/{answerId}/replies [post]
func (h *Handler) CreateReply(c *gin.Context) {
	questionId, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid question ID"})
		return
	}

	answerId, err := gocql.ParseUUID(c.Param("answerId"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid answer ID"})
		return
	}

	var reply models.AnswerReply
	if err := c.ShouldBindJSON(&reply); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if reply.Content == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Reply content is required"})
		return
	}
	if reply.AuthorID <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Author ID must be a positive integer"})
		return
	}

	if err := h.repo.AddReply(questionId, answerId, &reply); err != nil {
		if err.Error() == fmt.Sprintf("answer with ID %v not found in question %v", answerId, questionId) {
			c.JSON(http.StatusNotFound, gin.H{"error": "Answer not found"})
			return
		}
		log.Printf("Error adding reply to answer %v in question %v: %v", answerId, questionId, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, reply)
}

// @Summary Update a reply
// @Description Updates an existing reply to an answer within a question
// @Tags Replies
// @Accept json
// @Produce json
// @Param id path string true "Question ID"
// @Param answerId path string true "Answer ID"
// @Param replyId path string true "Reply ID"
// @Param reply body models.AnswerReply true "Updated reply data"
// @Success 200 {object} models.AnswerReply "Updated reply"
// @Failure 400 {object} map[string]string "Invalid question ID, answer ID, reply ID, or request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/answers/{answerId}/replies/{replyId} [put]
func (h *Handler) UpdateReply(c *gin.Context) {
	questionId, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid question ID"})
		return
	}

	answerId, err := gocql.ParseUUID(c.Param("answerId"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid answer ID"})
		return
	}

	replyId, err := gocql.ParseUUID(c.Param("replyId"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid reply ID"})
		return
	}

	var updatedReply models.AnswerReply
	if err := c.ShouldBindJSON(&updatedReply); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if updatedReply.Content == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Reply content is required"})
		return
	}

	if err := h.repo.UpdateReply(questionId, answerId, replyId, &updatedReply); err != nil {
		if err.Error() == fmt.Sprintf("answer with ID %v not found in question %v", answerId, questionId) {
			c.JSON(http.StatusNotFound, gin.H{"error": "Answer not found"})
			return
		}
		if err.Error() == fmt.Sprintf("reply with ID %v not found in answer %v", replyId, answerId) {
			c.JSON(http.StatusNotFound, gin.H{"error": "Reply not found"})
			return
		}
		log.Printf("Error updating reply %v in answer %v, question %v: %v", replyId, answerId, questionId, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	question, err := h.repo.GetQuestionByID(questionId)
	if err != nil {
		log.Printf("Error fetching question %v after updating reply: %v", questionId, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	for _, ans := range question.Answers {
		if ans.ID == answerId {
			for _, r := range ans.Replies {
				if r.ID == replyId {
					c.JSON(http.StatusOK, r)
					return
				}
			}
		}
	}
	c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve updated reply"})
}

// @Summary Delete a reply
// @Description Deletes a specific reply from an answer within a question
// @Tags Replies
// @Produce json
// @Param id path string true "Question ID"
// @Param answerId path string true "Answer ID"
// @Param replyId path string true "Reply ID"
// @Success 200 {object} map[string]string "Success message"
// @Failure 400 {object} map[string]string "Invalid question ID, answer ID, or reply ID"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/answers/{answerId}/replies/{replyId} [delete]
func (h *Handler) DeleteReply(c *gin.Context) {
	questionId, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid question ID"})
		return
	}

	answerId, err := gocql.ParseUUID(c.Param("answerId"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid answer ID"})
		return
	}

	replyId, err := gocql.ParseUUID(c.Param("replyId"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid reply ID"})
		return
	}

	if err := h.repo.DeleteReply(questionId, answerId, replyId); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Reply deleted successfully"})
}
