"""
Kafka Consumer Runner

Consumes transaction events from Kafka and processes them in real-time.
"""

from streaming.kafka_consumer import TransactionConsumer
import logging
import signal
import sys
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

consumer = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("Shutting down consumer...")
    if consumer:
        consumer.close()
    sys.exit(0)

def main():
    """Main consumer function"""
    global consumer
    
    signal.signal(signal.SIGINT, signal_handler)
    
    bootstrap_servers = 'localhost:9092'
    topic = 'transactions'
    group_id = 'transaction-consumer-group'
    
    consumer = TransactionConsumer(
        bootstrap_servers=bootstrap_servers,
        topic=topic,
        group_id=group_id
    )
    
    logger.info(f"Starting Kafka Consumer from {bootstrap_servers}")
    logger.info(f"Topic: {topic}")
    logger.info(f"Consumer Group: {group_id}")
    logger.info("Press Ctrl+C to stop\n")
    
    try:
        consumer.consume_messages()
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    finally:
        stats = consumer.get_stats()
        logger.info(f"\nFinal Statistics: {json.dumps(stats, indent=2)}")

if __name__ == "__main__":
    main()
