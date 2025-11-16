.PHONY: help producer consumer dashboard clean logs

help:
	@echo "Real-Time Streaming Pipeline"
	@echo "============================"
	@echo "make producer   - Start Kafka producer"
	@echo "make consumer   - Start Kafka consumer"
	@echo "make dashboard  - Start Jupyter dashboard"
	@echo "make kafka      - Start Kafka & Zookeeper (requires docker-compose)"
	@echo "make logs       - View streaming logs"
	@echo "make clean      - Clean up temporary files"

producer:
	python run_producer.py

consumer:
	python run_consumer.py

dashboard:
	jupyter notebook dashboards/

kafka:
	docker-compose -f docker-compose-kafka.yml up -d

logs:
	tail -f logs/*.log

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
