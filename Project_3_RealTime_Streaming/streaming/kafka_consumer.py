"""
Kafka Consumer Module

Consumes transaction events from Kafka for real-time processing and analytics.
"""

import json
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

class TransactionConsumer:
    """Kafka consumer for transaction events"""
    
    def __init__(self, bootstrap_servers='localhost:9092', topic='transactions', group_id='transaction-group'):
        """Initialize Kafka consumer"""
        self.topic = topic
        self.group_id = group_id
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            session_timeout_ms=6000
        )
        self.message_count = 0
        self.stats = {
            'total_messages': 0,
            'successful': 0,
            'failed': 0,
            'total_amount': 0
        }
        logger.info(f"Kafka Consumer initialized for topic: {topic}, group: {group_id}")
    
    def process_message(self, message):
        """Process individual message"""
        try:
            logger.debug(f"Processing message: {message}")
            
            # Update stats
            self.stats['total_messages'] += 1
            
            if message.get('status') == 'success':
                self.stats['successful'] += 1
                self.stats['total_amount'] += message.get('amount', 0)
            else:
                self.stats['failed'] += 1
            
            return True
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return False
    
    def consume_messages(self, max_messages=None):
        """Consume messages from Kafka"""
        logger.info(f"Starting to consume messages from {self.topic}...")
        
        try:
            for message in self.consumer:
                self.message_count += 1
                
                # Process message
                self.process_message(message.value)
                
                # Log periodically
                if self.message_count % 100 == 0:
                    logger.info(
                        f"Processed {self.message_count} messages. "
                        f"Successful: {self.stats['successful']}, "
                        f"Failed: {self.stats['failed']}"
                    )
                
                # Stop if max messages reached
                if max_messages and self.message_count >= max_messages:
                    logger.info(f"Reached max messages: {max_messages}")
                    break
        
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except Exception as e:
            logger.error(f"Error consuming messages: {str(e)}")
        finally:
            self.close()
    
    def consume_messages_async(self, callback=None, max_messages=None):
        """Consume messages asynchronously"""
        def consume_worker():
            self.consume_messages(max_messages)
        
        thread = threading.Thread(target=consume_worker, daemon=True)
        thread.start()
        return thread
    
    def get_stats(self):
        """Get consumption statistics"""
        return {
            'messages_processed': self.message_count,
            'stats': self.stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def close(self):
        """Close consumer"""
        self.consumer.close()
        logger.info(f"Consumer closed. Total messages: {self.message_count}")
        logger.info(f"Stats: {self.get_stats()}")

def main():
    """Main function for testing"""
    import sys
    
    max_msgs = int(sys.argv[1]) if len(sys.argv) > 1 else None
    
    consumer = TransactionConsumer()
    
    try:
        consumer.consume_messages(max_messages=max_msgs)
    except KeyboardInterrupt:
        print("Consumer stopped")
    finally:
        stats = consumer.get_stats()
        print(f"\n✓ Consumer stats: {json.dumps(stats, indent=2)}")

if __name__ == "__main__":
    main()
