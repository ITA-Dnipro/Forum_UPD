package repository

import (
	"testing"
	"time"

	"github.com/boghtml/qa-forum-service/internal/models"
	"github.com/gocql/gocql"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type Query interface {
	Exec() error
	Scan(dest ...interface{}) error
	Bind(...interface{}) Query
	PageSize(int) Query
	PageState([]byte) Query
	Consistency(gocql.Consistency) Query
}

type Session interface {
	Query(stmt string, values ...interface{}) Query
	Close()
}

type MockSession struct {
	mock.Mock
}

func (m *MockSession) Query(stmt string, values ...interface{}) Query {

	args := m.Called(stmt, values)

	return args.Get(0).(Query)
}

func (m *MockSession) Close() {
	m.Called()
}

type MockQuery struct {
	mock.Mock
}

func (mq *MockQuery) Exec() error {
	args := mq.Called()
	return args.Error(0)
}

func (mq *MockQuery) Scan(dest ...interface{}) error {
	args := mq.Called(dest)
	return args.Error(0)
}

func (mq *MockQuery) Bind(vals ...interface{}) Query {
	args := mq.Called(vals)
	return args.Get(0).(Query)
}

func (mq *MockQuery) PageSize(size int) Query {
	args := mq.Called(size)
	return args.Get(0).(Query)
}

func (mq *MockQuery) PageState(state []byte) Query {
	args := mq.Called(state)
	return args.Get(0).(Query)
}

func (mq *MockQuery) Consistency(c gocql.Consistency) Query {
	args := mq.Called(c)
	return args.Get(0).(Query)
}

type testScyllaDB struct {
	session Session
}

func (db *testScyllaDB) CreateQuestion(q *models.Question) error {
	if q.ID == (gocql.UUID{}) {
		q.ID = gocql.TimeUUID()
	}
	q.CreatedAt = time.Now()
	q.UpdatedAt = time.Now()
	if q.Status == "" {
		q.Status = "open"
	}

	mainQuery := `INSERT INTO questions (
        question_id, author_id, title, description, status,
        created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?)`

	err := db.session.
		Query(mainQuery, q.ID, q.AuthorID, q.Title, q.Description, q.Status, q.CreatedAt, q.UpdatedAt).
		Exec()
	if err != nil {
		return err
	}

	secondQuery := `INSERT INTO questions_by_author (...) VALUES (...)`
	err = db.session.
		Query(secondQuery, q.AuthorID, q.ID, q.Title).
		Exec()
	if err != nil {
		return err
	}

	return nil
}

func TestCreateQuestion_Success(t *testing.T) {
	mockSession := new(MockSession)
	db := &testScyllaDB{session: mockSession}

	question := &models.Question{
		Title:       "Test",
		Description: "Desc",
		AuthorID:    1,
	}

	mockQuery := new(MockQuery)

	mockSession.On("Query", mock.Anything, mock.Anything).Return(mockQuery).Twice()

	mockQuery.On("Exec").Return(nil).Twice()

	mockQuery.On("Bind", mock.Anything).Return(mockQuery).Maybe()
	mockQuery.On("PageSize", mock.Anything).Return(mockQuery).Maybe()
	mockQuery.On("PageState", mock.Anything).Return(mockQuery).Maybe()
	mockQuery.On("Consistency", mock.Anything).Return(mockQuery).Maybe()

	err := db.CreateQuestion(question)

	assert.NoError(t, err)
	assert.NotEqual(t, gocql.UUID{}, question.ID, "question.ID should be set")
	assert.Equal(t, "open", question.Status, "question.Status default to open")

	mockSession.AssertExpectations(t)
	mockQuery.AssertExpectations(t)
}
