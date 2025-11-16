.PHONY: help install test run clean lint format

help:
	@echo "Kenyan Market ETL Pipeline - Available Commands"
	@echo "================================================"
	@echo "make install  - Install project dependencies"
	@echo "make test     - Run unit tests"
	@echo "make run      - Execute ETL pipeline"
	@echo "make lint     - Run code linting"
	@echo "make format   - Format code with black"
	@echo "make clean    - Remove generated files"

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

run:
	python run_pipeline.py

lint:
	flake8 etl/ config/ --max-line-length=120

format:
	black etl/ config/ tests/ --line-length=120

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/

requirements:
	pip freeze > requirements.txt
