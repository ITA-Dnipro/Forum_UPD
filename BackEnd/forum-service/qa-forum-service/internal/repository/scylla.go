package repository

import (
	"log"
	"strings"
	"time"

	"github.com/gocql/gocql"
)

type ScyllaDB struct {
	session *gocql.Session
}

func NewScyllaDB(hosts string, keyspace string) (*ScyllaDB, error) {

	cluster := gocql.NewCluster(strings.Split(hosts, ",")...)
	cluster.Keyspace = keyspace
	cluster.Consistency = gocql.Quorum
	cluster.ConnectTimeout = time.Second * 10
	cluster.Timeout = time.Second * 10
	cluster.RetryPolicy = &gocql.SimpleRetryPolicy{NumRetries: 3}

	session, err := cluster.CreateSession()
	if err != nil {
		log.Printf("Failed to connect to ScyllaDB: %v", err)

		if session != nil {
			session.Close()
		}
		return nil, err
	}

	return &ScyllaDB{session: session}, nil
}

func (db *ScyllaDB) GetSession() *gocql.Session {
	return db.session
}

func (db *ScyllaDB) Close() {
	if db.session != nil {
		db.session.Close()
	}
}
