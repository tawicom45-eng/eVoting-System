.PHONY: help setup run test logs clean init

help:
	@echo "M-Pesa Airflow Pipeline"
	@echo "======================"
	@echo "make init       - Initialize Airflow"
	@echo "make setup      - Setup environment"
	@echo "make run        - Start Airflow services"
	@echo "make test       - Run tests"
	@echo "make logs       - View Airflow logs"
	@echo "make clean      - Clean up"

setup:
	pip install -r requirements.txt

init:
	airflow db init
	airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com

run:
	docker-compose -f docker-compose-airflow.yml up

test:
	python -m pytest tests/ -v

logs:
	tail -f logs/*.log

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
