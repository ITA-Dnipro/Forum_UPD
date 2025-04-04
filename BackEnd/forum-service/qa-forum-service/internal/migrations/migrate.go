package migrations

import (
	"fmt"
	"io/ioutil"
	"log"
	"path/filepath"
	"strings"

	"github.com/gocql/gocql"
)

func RunMigrations(session *gocql.Session, migrationsDir string) error {

	if err := session.Query("SELECT release_version FROM system.local").Exec(); err != nil {
		return fmt.Errorf("failed to verify connection: %v", err)
	}

	files, err := ioutil.ReadDir(migrationsDir)
	if err != nil {
		return fmt.Errorf("failed to read migrations directory: %v", err)
	}

	for _, f := range files {
		if filepath.Ext(f.Name()) == ".cql" {
			path := filepath.Join(migrationsDir, f.Name())
			content, err := ioutil.ReadFile(path)
			if err != nil {
				return fmt.Errorf("failed to read file %s: %v", f.Name(), err)
			}

			statements := strings.Split(string(content), ";")
			for _, st := range statements {
				stmt := strings.TrimSpace(st)
				if stmt == "" {
					continue
				}
				log.Printf("Executing migration from %s:\n%s", f.Name(), stmt)

				if err := session.Query(stmt).Exec(); err != nil {
					return fmt.Errorf("migration error in file %s: %v", f.Name(), err)
				}
			}
		}
	}

	return nil
}
