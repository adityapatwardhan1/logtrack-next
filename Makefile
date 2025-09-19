.PHONY: reinit init-db reset-db ingest-detect ingest detect test docker-up docker-down venv activate user show dash clear-alerts clear-logs

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
	PYTHONPATH=. python3 cli/ingest_logs.py $(file)
	PYTHONPATH=. python3 cli/run_detection.py

ingest:
	PYTHONPATH=. python3 cli/ingest_logs.py $(file)
	PYTHONPATH=. python3 cli/show_logs.py

print:
	PYTHONPATH=. python3 cli/show_logs.py

dash:
	. venv/bin/activate && PYTHONPATH=. streamlit run dashboard/app.py

detect:
	PYTHONPATH=. python3 cli/run_detection.py

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