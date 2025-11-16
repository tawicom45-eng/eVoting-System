"""
Kafka Producer Module

Produces transaction events to Kafka topics for real-time streaming processing.
"""

import json
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
from datetime import datetime
import random
import uuid

logger = logging.getLogger(__name__)

class TransactionProducer:
    """Kafka producer for transaction events"""
    
    def __init__(self, bootstrap_servers='localhost:9092', topic='transactions'):
        """Initialize Kafka producer"""
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3,
            compression_type='gzip'
        )
        logger.info(f"Kafka Producer initialized for topic: {topic}")
    
    def generate_transaction(self):
        """Generate a random transaction"""
        return {
            'transaction_id': str(uuid.uuid4()),
            'sender': f'254{random.randint(700000000, 799999999)}',
            'receiver': f'254{random.randint(700000000, 799999999)}',
            'amount': round(random.uniform(100, 50000), 2),
            'timestamp': datetime.now().isoformat(),
            'transaction_type': random.choice(['transfer', 'withdrawal', 'deposit']),
            'status': random.choices(['success', 'failed'], weights=[90, 10])[0],
            'provider': random.choice(['Safaricom', 'Airtel', 'Equity']),
            'fee': round(random.uniform(0, 100), 2)
        }
    
    def send_transaction(self, transaction=None, callback=None):
        """Send transaction to Kafka"""
        if transaction is None:
            transaction = self.generate_transaction()
        
        try:
            future = self.producer.send(self.topic, value=transaction)
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Message sent to topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}"
            )
            
            if callback:
                callback(transaction)
            
            return True
        except KafkaError as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    def send_batch(self, count=100):
        """Send batch of transactions"""
        logger.info(f"Sending batch of {count} transactions...")
        
        success_count = 0
        for i in range(count):
            if self.send_transaction():
                success_count += 1
            
            if (i + 1) % 10 == 0:
                logger.info(f"Sent {i + 1}/{count} transactions")
        
        logger.info(f"Batch complete. Successful: {success_count}/{count}")
        return success_count
    
    def flush(self, timeout=10):
        """Flush pending messages"""
        self.producer.flush(timeout)
        logger.info("Producer flushed")
    
    def close(self):
        """Close producer"""
        self.producer.close()
        logger.info("Kafka Producer closed")

def main():
    """Main function for testing"""
    import sys
    import time
    
    producer = TransactionProducer()
    
    try:
        # Send continuous stream
        message_count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
        
        for i in range(message_count):
            producer.send_transaction()
            print(f"Sent message {i + 1}/{message_count}")
            time.sleep(1)
        
        producer.flush()
        print("✓ All messages sent successfully")
    
    except KeyboardInterrupt:
        print("Producer stopped by user")
    finally:
        producer.close()

if __name__ == "__main__":
    main()
