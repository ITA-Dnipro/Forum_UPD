package repository_test

import (
	"fmt"
	"testing"

	"github.com/boghtml/qa-forum-service/internal/repository"
	"github.com/gocql/gocql"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type PinRepository interface {
	PinAnswer(questionID, answerID gocql.UUID, userID int) error
	UnpinAnswer(questionID, answerID gocql.UUID, userID int) error
}

type testPinDB struct {
	session repository.Session
}

func (db *testPinDB) PinAnswer(questionID, answerID gocql.UUID, userID int) error {

	selQuery := `SELECT author_id, accepted_answer_ids FROM questions WHERE question_id=?`
	q := db.session.Query(selQuery, questionID)
	var authorID int
	var accepted []gocql.UUID
	if err := q.Scan(&authorID, &accepted); err != nil {
		if err == gocql.ErrNotFound {
			return fmt.Errorf("question not found")
		}
		return err
	}

	if authorID != userID {
		return fmt.Errorf("only author can pin")
	}

	for _, ans := range accepted {
		if ans == answerID {
			return fmt.Errorf("answer already pinned")
		}
	}
	accepted = append(accepted, answerID)

	upd := db.session.Query(`UPDATE questions SET accepted_answer_ids=? WHERE question_id=?`, accepted, questionID)
	if err := upd.Exec(); err != nil {
		return err
	}

	return nil
}

func (db *testPinDB) UnpinAnswer(questionID, answerID gocql.UUID, userID int) error {
	return nil
}

type MockSession struct {
	mock.Mock
}

func (m *MockSession) Query(stmt string, vals ...interface{}) repository.Query {
	args := m.Called(stmt, vals)
	return args.Get(0).(repository.Query)
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
func (mq *MockQuery) Bind(vals ...interface{}) repository.Query {
	args := mq.Called(vals)
	return args.Get(0).(repository.Query)
}
func (mq *MockQuery) PageSize(i int) repository.Query {
	args := mq.Called(i)
	return args.Get(0).(repository.Query)
}
func (mq *MockQuery) PageState(b []byte) repository.Query {
	args := mq.Called(b)
	return args.Get(0).(repository.Query)
}
func (mq *MockQuery) Consistency(c gocql.Consistency) repository.Query {
	args := mq.Called(c)
	return args.Get(0).(repository.Query)
}

func TestPinAnswer_Success(t *testing.T) {
	mockSession := new(MockSession)
	db := &testPinDB{session: mockSession}

	selectQ := new(MockQuery)
	updateQ := new(MockQuery)

	mockSession.On("Query", mock.Anything, mock.Anything).Return(selectQ).Once()

	selectQ.On("Scan", mock.Anything).Return(nil).Run(func(args mock.Arguments) {
		dest := args.Get(0).([]interface{})

		*(dest[0].(*int)) = 111
		*(dest[1].(*[]gocql.UUID)) = []gocql.UUID{}
	})

	mockSession.On("Query", mock.Anything, mock.Anything).Return(updateQ).Once()

	updateQ.On("Exec").Return(nil)

	questionID := gocql.TimeUUID()
	answerID := gocql.TimeUUID()
	err := db.PinAnswer(questionID, answerID, 111)
	assert.NoError(t, err)

	mockSession.AssertExpectations(t)
	selectQ.AssertExpectations(t)
	updateQ.AssertExpectations(t)
}

func TestPinAnswer_NotAuthor(t *testing.T) {
	mockSession := new(MockSession)
	db := &testPinDB{session: mockSession}

	selectQ := new(MockQuery)
	mockSession.On("Query", mock.Anything, mock.Anything).Return(selectQ).Once()

	selectQ.On("Scan", mock.Anything).Return(nil).Run(func(args mock.Arguments) {
		dest := args.Get(0).([]interface{})
		*(dest[0].(*int)) = 777
		*(dest[1].(*[]gocql.UUID)) = []gocql.UUID{}
	})

	questionID := gocql.TimeUUID()
	answerID := gocql.TimeUUID()
	err := db.PinAnswer(questionID, answerID, 999)
	assert.EqualError(t, err, "only author can pin")

	mockSession.AssertExpectations(t)
	selectQ.AssertExpectations(t)
}
