.PHONY: help setup run test clean

help:
	@echo "Safaricom Data Warehouse ETL"
	@echo "============================="
	@echo "make setup     - Install dependencies"
	@echo "make run       - Execute ETL pipeline"
	@echo "make test      - Run tests"
	@echo "make clean     - Clean temporary files"

setup:
	pip install -r requirements.txt

run:
	python warehouse_etl.py

test:
	python -m pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
