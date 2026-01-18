.PHONY: reinit init-db reset-db ingest-detect ingest detect test docker-up docker-down venv activate user show dash clear-alerts clear-logs
FILE ?=
EMIT_ARTIFACTS ?=

reinit:
	PYTHONPATH=. python3 db/reset_db.py
	PYTHONPATH=. python3 db/init_db.py
	PYTHONPATH=. python3 migrate_rules.py

init-db:
	PYTHONPATH=. python3 db/init_db.py
	PYTHONPATH=. python3 migrate_rules.py

reset-db:
	PYTHONPATH=. python3 db/reset_db.py

ingest-detect:
	PYTHONPATH=. python3 cli/ingest_logs.py $(FILE) $(ARTIFACT_FLAG)
	PYTHONPATH=. python3 cli/run_detection.py $(ARTIFACT_FLAG)

ingest:
	PYTHONPATH=. python3 cli/ingest_logs.py $(FILE) $(ARTIFACT_FLAG)
	PYTHONPATH=. python3 cli/show_logs.py

print:
	PYTHONPATH=. python3 cli/show_logs.py

dash:
	. venv/bin/activate && PYTHONPATH=. streamlit run dashboard/app.py

detect:
	PYTHONPATH=. python3 cli/run_detection.py $(ARTIFACT_FLAG)

test:
	PYTHONPATH=. pytest -q

docker-up:
	docker compose up --build

docker-down:
	docker compose down

venv:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt

clear-alerts:
	PYTHONPATH=. python3 cli/cleanup.py alerts

clear-logs:
	PYTHONPATH=. python3 cli/cleanup.py logs $(hours)

activate:
	@echo "Each make command creates its own shell so you need to activate the venv manually."
	@echo "Run the following to activate the virtual environment:"
	@echo "source venv/bin/activate"

role ?= user
user:
	@stty -echo; \
	read -p "Password for $(username): " password; echo; \
	stty echo; \
	PYTHONPATH=. python3 cli/create_user.py $(username) $$password -r $(role)

assert-golden:
	diff -bB samples/expected/clf_parsed.json artifacts/parsed/clf_parsed.json
	@echo "Golden path verified: parsed output matches expected."

assert-alerts:
	diff -bB samples/expected/clf_alerts.json artifacts/alerts/clf_alerts.json
	@echo "Golden path verified: alert output matches expected."

ci-e2e:
	$(MAKE) reinit
	$(MAKE) ingest FILE=samples/clf_golden.clf EMIT_ARTIFACTS=1
	$(MAKE) detect EMIT_ARTIFACTS=1
	$(MAKE) assert-golden
	$(MAKE) assert-alerts
