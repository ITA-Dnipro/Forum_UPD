package migrations

import (
	"github.com/gocql/gocql"
)

func CreateKeyspace(session *gocql.Session, keyspaceName string) error {

	query := `CREATE KEYSPACE IF NOT EXISTS ` + keyspaceName + ` 
             WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}`

	return session.Query(query).Exec()
}
