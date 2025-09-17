.PHONY: init-db reset-db ingest run-detection test venv activate docker-up docker-down 

init-db:
	PYTHONPATH=. python3 db/init_db.py
	PYTHONPATH=. python3 migrate_rules.py

reset-db:
	PYTHONPATH=. python3 db/reset_db.py

ingest:
	PYTHONPATH=. python3 cli/ingest_logs.py $(file)
	PYTHONPATH=. python3 cli/show_logs.py

detect:
	PYTHONPATH=. python3 cli/run_detection.py

test:
	PYTHONPATH=. pytest -q

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

venv:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt

activate:
	@echo "Each make command creates its own shell so you need to activate the venv manually."
	@echo "Run the following to activate the virtual environment:"
	@echo "source venv/bin/activate"