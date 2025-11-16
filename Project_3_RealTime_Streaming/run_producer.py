"""
Kafka Producer Runner

Continuously produces transaction data to Kafka topics for streaming pipeline.
"""

from streaming.kafka_producer import TransactionProducer
import time
import logging
import signal
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

producer = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("Shutting down producer...")
    if producer:
        producer.close()
    sys.exit(0)

def main():
    """Main producer function"""
    global producer
    
    signal.signal(signal.SIGINT, signal_handler)
    
    bootstrap_servers = 'localhost:9092'
    topic = 'transactions'
    interval = 1  # Seconds between messages
    
    producer = TransactionProducer(bootstrap_servers=bootstrap_servers, topic=topic)
    
    logger.info(f"Starting Kafka Producer to {bootstrap_servers} on topic '{topic}'")
    logger.info("Press Ctrl+C to stop\n")
    
    message_count = 0
    
    try:
        while True:
            message_count += 1
            transaction = producer.generate_transaction()
            
            if producer.send_transaction(transaction):
                logger.info(f"[{message_count}] Sent: {transaction['transaction_id']} | "
                          f"Amount: {transaction['amount']} | Status: {transaction['status']}")
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        logger.info("Producer stopped by user")
    finally:
        producer.flush()
        producer.close()
        logger.info(f"Total messages sent: {message_count}")

if __name__ == "__main__":
    main()
