package hooks

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strings"

	"github.com/labstack/echo/v5"
	"github.com/pocketbase/dbx"
	"github.com/pocketbase/pocketbase"
	"github.com/pocketbase/pocketbase/apis"
	"github.com/pocketbase/pocketbase/core"
	"github.com/pocketbase/pocketbase/models"
	"golang.org/x/exp/slices"
)

func Register(app *pocketbase.PocketBase) error {
	modelHandler := func(event string) func(e *core.ModelEvent) error {
		return func(e *core.ModelEvent) error {
			table := e.Model.TableName()
			// we don't want to executeEventActions if the event is a system event (e.g. "_collections" changes)
			if record, ok := e.Model.(*models.Record); ok {
				executeEventActions(app, event, table, record)
			} else {
				log.Println("Skipping executeEventActions for table:", table)
			}
			return nil
		}
	}
	app.OnBeforeServe().Add(func(e *core.ServeEvent) error {
		app.OnModelAfterCreate().Add(modelHandler("insert"))
		app.OnModelAfterUpdate().Add(modelHandler("update"))
		app.OnModelAfterDelete().Add(modelHandler("delete"))
		app.OnRecordAfterCreateRequest().Add(func(e *core.RecordCreateEvent) error {
			return doAudit(app, "insert", e.Record, e.HttpContext)
		})
		app.OnRecordAfterUpdateRequest().Add(func(e *core.RecordUpdateEvent) error {
			return doAudit(app, "update", e.Record, e.HttpContext)
		})
		app.OnRecordAfterDeleteRequest().Add(func(e *core.RecordDeleteEvent) error {
			return doAudit(app, "delete", e.Record, e.HttpContext)
		})
		return nil
	})
	return nil
}

// collection names to be audit logged
var collections = strings.Split(os.Getenv("AUDITLOG"), ",")

func doAudit(app *pocketbase.PocketBase, event string, record *models.Record, ctx echo.Context) error {
	collection := record.Collection().Name
	// exclude logging "auditlog" and include only what's in AUDITLOG env var
	if collection != "auditlog" && slices.Contains(collections, collection) {
		var user, admin string
		if u, ok := ctx.Get(apis.ContextAdminKey).(*models.Admin); ok {
			admin = u.Id
		}
		if u, ok := ctx.Get(apis.ContextAuthRecordKey).(*models.Record); ok {
			user = u.Id
		}
		log.Printf("AuditLog:%s:%s:%s:%s:%s\n", collection, record.Id, event, user, admin)
		target, err := app.Dao().FindCollectionByNameOrId("auditlog")
		if err != nil {
			return err
		}
		auditlog := models.NewRecord(target)
		auditlog.Set("collection", collection)
		auditlog.Set("record", record.Id)
		auditlog.Set("event", event)
		auditlog.Set("user", user)
		auditlog.Set("admin", admin)
		auditlog.Set("data", record)

		return app.Dao().SaveRecord(auditlog)
	}
	return nil
}

func executeEventActions(app *pocketbase.PocketBase, event string, table string, record *models.Record) {
	// TODO: Load and cache this. Reload only on changes to "hooks" table
	rows := []dbx.NullStringMap{}
	app.DB().Select("action_type", "action", "action_params", "expands").
		From("hooks").
		Where(dbx.HashExp{"collection": table, "event": event, "disabled": false}).
		All(&rows)
	for _, row := range rows {
		action_type := row["action_type"].String
		action := row["action"].String
		action_params := row["action_params"].String
		expands := strings.Split(row["expands"].String, ",")
		app.Dao().ExpandRecord(record, expands, func(c *models.Collection, ids []string) ([]*models.Record, error) {
			return app.Dao().FindRecordsByIds(c.Name, ids, nil)
		})
		if err := executeEventAction(event, table, action_type, action, action_params, record); err != nil {
			log.Println("ERROR", err)
		}
	}
}

func executeEventAction(event, table, action_type, action, action_params string, record *models.Record) error {
	log.Printf("event:%s, table: %s, action: %s\n", event, table, action)
	switch action_type {
	case "command":
		return doCommand(action, action_params, record)
	case "post":
		return doPost(action, action_params, record)
	default:
		return errors.New(fmt.Sprintf("Unknown action_type: %s", action_type))
	}
}

func doCommand(action, action_params string, record *models.Record) error {
	cmd := exec.Command(action, action_params)
	if w, err := cmd.StdinPipe(); err != nil {
		return err
	} else {
		if r, err := cmd.StdoutPipe(); err != nil {
			return err
		} else {
			go func() {
				defer w.Close()
				defer r.Close()
				log.Println("-------------------------------")
				defer log.Println("-------------------------------")
				if err := cmd.Start(); err != nil {
					log.Printf("command start failed: %s %+v\n", action, err)
				} else {
					// write JSON into the pipe and close
					json.NewEncoder(w).Encode(record)
					w.Close()
					if err := cmd.Wait(); err != nil {
						log.Printf("command wait failed: %s %+v\n", action, err)
					}
				}
			}()
			// read pipe's stdout and copy to ours (in parallel to the above goroutine)
			io.Copy(os.Stdout, r)
		}
	}
	return nil
}

func doPost(action, action_params string, record *models.Record) error {
	r, w := io.Pipe()
	defer w.Close()
	go func() {
		defer r.Close()
		if resp, err := http.Post(action, "application/json", r); err != nil {
			log.Println("POST failed", action, err)
		} else {
			io.Copy(os.Stdout, resp.Body)
		}
	}()
	if err := json.NewEncoder(w).Encode(record); err != nil {
		log.Println("ERROR writing to pipe", err)
	}
	return nil
}
