package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/boghtml/qa-forum-service/internal/models"
	"github.com/gin-gonic/gin"
	"github.com/gocql/gocql"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockRepository struct {
	mock.Mock
}

func (m *MockRepository) CreateQuestion(q *models.Question) error {
	args := m.Called(q)
	return args.Error(0)
}

func (m *MockRepository) GetQuestionsByAuthor(authorID int, limit int, pagingState []byte) ([]models.Question, []byte, error) {
	args := m.Called(authorID, limit, pagingState)
	return args.Get(0).([]models.Question), args.Get(1).([]byte), args.Error(2)
}

func (m *MockRepository) GetQuestionsByStatus(status string, limit int, pagingState []byte) ([]models.Question, []byte, error) {
	args := m.Called(status, limit, pagingState)
	return args.Get(0).([]models.Question), args.Get(1).([]byte), args.Error(2)
}

func (m *MockRepository) GetAllQuestions(limit int, pagingState []byte) ([]models.Question, []byte, error) {
	args := m.Called(limit, pagingState)
	return args.Get(0).([]models.Question), args.Get(1).([]byte), args.Error(2)
}

func (m *MockRepository) GetQuestionByID(id gocql.UUID) (*models.Question, error) {
	args := m.Called(id)
	return args.Get(0).(*models.Question), args.Error(1)
}

func (m *MockRepository) UpdateQuestion(q *models.Question) error {
	args := m.Called(q)
	return args.Error(0)
}

func (m *MockRepository) DeleteQuestion(id gocql.UUID) error {
	args := m.Called(id)
	return args.Error(0)
}

func (m *MockRepository) SaveQuestion(userID int, questionID gocql.UUID) error {
	args := m.Called(userID, questionID)
	return args.Error(0)
}

func (m *MockRepository) GetSavedQuestions(userID int, limit int, pagingState []byte) ([]models.Question, []byte, error) {
	args := m.Called(userID, limit, pagingState)
	return args.Get(0).([]models.Question), args.Get(1).([]byte), args.Error(2)
}

func (m *MockRepository) UnsaveQuestion(userID int, questionID gocql.UUID) error {
	args := m.Called(userID, questionID)
	return args.Error(0)
}

func (m *MockRepository) AddAnswer(questionId gocql.UUID, answer *models.QuestionAnswer) error {
	args := m.Called(questionId, answer)
	return args.Error(0)
}

func (m *MockRepository) UpdateAnswer(questionId gocql.UUID, answerId gocql.UUID, updatedAnswer *models.QuestionAnswer) error {
	args := m.Called(questionId, answerId, updatedAnswer)
	return args.Error(0)
}

func (m *MockRepository) DeleteAnswer(questionId gocql.UUID, answerId gocql.UUID) error {
	args := m.Called(questionId, answerId)
	return args.Error(0)
}

func (m *MockRepository) AddReaction(userID int, questionID gocql.UUID, isLike bool) error {
	args := m.Called(userID, questionID, isLike)
	return args.Error(0)
}

func (m *MockRepository) RemoveReaction(userID int, questionID gocql.UUID) error {
	args := m.Called(userID, questionID)
	return args.Error(0)
}

func (m *MockRepository) GetReactions(questionID gocql.UUID) ([]models.ReactionDetail, error) {
	args := m.Called(questionID)
	return args.Get(0).([]models.ReactionDetail), args.Error(1)
}

func (m *MockRepository) GetLikedQuestions(userID int, limit int, pagingState []byte) ([]models.Question, []byte, error) {
	args := m.Called(userID, limit, pagingState)
	return args.Get(0).([]models.Question), args.Get(1).([]byte), args.Error(2)
}

func (m *MockRepository) GetDislikedQuestions(userID int, limit int, pagingState []byte) ([]models.Question, []byte, error) {
	args := m.Called(userID, limit, pagingState)
	return args.Get(0).([]models.Question), args.Get(1).([]byte), args.Error(2)
}

func (m *MockRepository) AddReply(questionId, answerId gocql.UUID, reply *models.AnswerReply) error {
	args := m.Called(questionId, answerId, reply)
	return args.Error(0)
}

func (m *MockRepository) UpdateReply(questionId, answerId, replyId gocql.UUID, updatedReply *models.AnswerReply) error {
	args := m.Called(questionId, answerId, replyId, updatedReply)
	return args.Error(0)
}

func (m *MockRepository) DeleteReply(questionId, answerId, replyId gocql.UUID) error {
	args := m.Called(questionId, answerId, replyId)
	return args.Error(0)
}

func (m *MockRepository) AddAnswerReaction(questionId, answerId gocql.UUID, userID int, isLike bool) error {
	args := m.Called(questionId, answerId, userID, isLike)
	return args.Error(0)
}

func (m *MockRepository) DeleteAnswerReaction(questionId, answerId gocql.UUID, userID int) error {
	args := m.Called(questionId, answerId, userID)
	return args.Error(0)
}

func (m *MockRepository) AddReplyReaction(questionId, answerId, replyId gocql.UUID, userID int, isLike bool) error {
	args := m.Called(questionId, answerId, replyId, userID, isLike)
	return args.Error(0)
}

func (m *MockRepository) DeleteReplyReaction(questionId, answerId, replyId gocql.UUID, userID int) error {
	args := m.Called(questionId, answerId, replyId, userID)
	return args.Error(0)
}

func (m *MockRepository) AcceptAnswer(questionId, answerId gocql.UUID, userID int) error {
	args := m.Called(questionId, answerId, userID)
	return args.Error(0)
}

func (m *MockRepository) UnacceptAnswer(questionId, answerId gocql.UUID, userID int) error {
	args := m.Called(questionId, answerId, userID)
	return args.Error(0)
}

func TestCreateQuestion_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()

	mockRepo := new(MockRepository)
	handler := NewHandler(mockRepo)

	router.POST("/api/questions", handler.CreateQuestion)

	reqBody := models.Question{
		Title:       "Test Question",
		Description: "Test Description",
		AuthorID:    1,
	}
	body, _ := json.Marshal(reqBody)

	mockRepo.On("CreateQuestion", mock.AnythingOfType("*models.Question")).Return(nil)

	req, _ := http.NewRequest("POST", "/api/questions", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusCreated, w.Code)
	var response models.Question
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, "Test Question", response.Title)
	assert.Equal(t, "Test Description", response.Description)
	assert.Equal(t, 1, response.AuthorID)
	mockRepo.AssertExpectations(t)
}

func TestCreateQuestion_InvalidInput(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()

	handler := NewHandler(new(MockRepository))
	router.POST("/api/questions", handler.CreateQuestion)

	reqBody := models.Question{
		Title:    "",
		AuthorID: 1,
	}
	body, _ := json.Marshal(reqBody)

	req, _ := http.NewRequest("POST", "/api/questions", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
	assert.JSONEq(t, `{"error": "Title and Description are required"}`, w.Body.String())
}

func TestGetQuestions_ByAuthor(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()

	mockRepo := new(MockRepository)
	handler := NewHandler(mockRepo)

	router.GET("/api/questions", handler.GetQuestions)

	questionID := gocql.TimeUUID()
	questions := []models.Question{{
		ID:            questionID,
		Title:         "Test",
		AuthorID:      0,           // Значення за замовчуванням
		Description:   "",          // Значення за замовчуванням
		Status:        "",          // Значення за замовчуванням
		LikesCount:    0,           // Значення за замовчуванням
		DislikesCount: 0,           // Значення за замовчуванням
		SavesCount:    0,           // Значення за замовчуванням
		CreatedAt:     time.Time{}, // 0001-01-01T00:00:00Z
		UpdatedAt:     time.Time{}, // 0001-01-01T00:00:00Z
	}}
	mockRepo.On("GetQuestionsByAuthor", 1, 10, []byte{}).Return(questions, []byte("paging"), nil)

	req, _ := http.NewRequest("GET", "/api/questions?author_id=1", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	expectedJSON := `{"questions": [{"id": "` + questionID.String() + `", "title": "Test", "author_id": 0, "description": "", "status": "", "likes_count": 0, "dislikes_count": 0, "saves_count": 0, "created_at": "0001-01-01T00:00:00Z", "updated_at": "0001-01-01T00:00:00Z"}],"paging_state": "706167696e67"}`
	assert.JSONEq(t, expectedJSON, w.Body.String())
	mockRepo.AssertExpectations(t)
}

func TestGetQuestion_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()

	mockRepo := new(MockRepository)
	handler := NewHandler(mockRepo)

	router.GET("/api/questions/:id", handler.GetQuestion)

	questionID := gocql.TimeUUID()
	question := &models.Question{
		ID:            questionID,
		Title:         "Test",
		AuthorID:      0,
		Description:   "",
		Status:        "",
		LikesCount:    0,
		DislikesCount: 0,
		SavesCount:    0,
		CreatedAt:     time.Time{},
		UpdatedAt:     time.Time{},
	}
	mockRepo.On("GetQuestionByID", questionID).Return(question, nil)

	req, _ := http.NewRequest("GET", "/api/questions/"+questionID.String(), nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	expectedJSON := `{"id": "` + questionID.String() + `", "title": "Test", "author_id": 0, "description": "", "status": "", "likes_count": 0, "dislikes_count": 0, "saves_count": 0, "created_at": "0001-01-01T00:00:00Z", "updated_at": "0001-01-01T00:00:00Z"}`
	assert.JSONEq(t, expectedJSON, w.Body.String())
	mockRepo.AssertExpectations(t)
}

func TestGetQuestion_NotFound(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()

	mockRepo := new(MockRepository)
	handler := NewHandler(mockRepo)

	router.GET("/api/questions/:id", handler.GetQuestion)

	questionID := gocql.TimeUUID()
	mockRepo.On("GetQuestionByID", questionID).Return((*models.Question)(nil), nil)

	req, _ := http.NewRequest("GET", "/api/questions/"+questionID.String(), nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
	assert.JSONEq(t, `{"error": "Question not found"}`, w.Body.String())
	mockRepo.AssertExpectations(t)
}
