.PHONY: init-db reset-db ingest run-detection test docker-up docker-down

init-db:
	PYTHONPATH=. python3 db/init_db.py
	PYTHONPATH=. python3 migrate_rules.py

reset-db:
	PYTHONPATH=. python3 db/reset_db.py

ingest:
	PYTHONPATH=. python3 cli/ingest_logs.py $(file)
	PYTHONPATH=. python3 cli/show_logs.py

run-detection:
	PYTHONPATH=. python3 cli/run_detection.py

test:
	PYTHONPATH=. pytest -q

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
