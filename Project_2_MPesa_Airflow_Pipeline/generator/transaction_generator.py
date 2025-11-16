"""
M-Pesa Transaction Generator

Generates synthetic M-Pesa transaction data for testing and development.
Supports custom transaction volumes and realistic distribution patterns.

Business Context:
- M-Pesa is Safaricom's mobile money service processing ~30M transactions/day in Kenya
- Transaction types: p2p transfers, merchant payments, airtime, bank deposits/withdrawals
- Key metrics: Success rate ~85%, failed ~10%, pending ~3%, reversed ~2%
- Amounts vary by type: transfers (100-50K KES), airtime (10-1K KES)
- Used for Airflow DAG testing, fraud detection model training, and reporting
"""

import json
import uuid
import random
from datetime import datetime, timedelta
from faker import Faker
import logging

logger = logging.getLogger(__name__)
fake = Faker('en_KE')  # Kenyan locale - generates realistic KE phone numbers and names

class TransactionGenerator:
    """Generate realistic M-Pesa transaction data"""
    
    TRANSACTION_TYPES = ['transfer', 'withdrawal', 'deposit', 'payment', 'airtime_purchase']
    STATUSES = ['success', 'failed', 'pending', 'reversed']
    PROVIDERS = ['Safaricom', 'Airtel', 'Equity', 'KCB', 'Standard_Chartered']
    
    # Realistic transaction amount distribution
    AMOUNT_RANGES = {
        'transfer': (100, 50000),
        'withdrawal': (500, 25000),
        'deposit': (1000, 100000),
        'payment': (50, 10000),
        'airtime_purchase': (10, 1000)
    }
    
    def __init__(self, start_date=None, end_date=None):
        """
        Initialize transaction generator
        
        Args:
            start_date: Start date for transactions (default: 30 days ago)
            end_date: End date for transactions (default: now)
        """
        self.end_date = end_date or datetime.now()
        self.start_date = start_date or (self.end_date - timedelta(days=30))
        
    def _generate_phone_number(self):
        """Generate realistic Kenyan phone number"""
        prefixes = ['254712', '254713', '254714', '254715', '254716', '254717', '254718', '254719']
        prefix = random.choice(prefixes)
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return prefix + suffix
    
    def _generate_transaction_id(self):
        """Generate unique transaction ID"""
        return f"TXN{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    def _get_random_timestamp(self):
        """Get random timestamp between start and end date"""
        time_between = (self.end_date - self.start_date).total_seconds()
        random_seconds = random.randint(0, int(time_between))
        return self.start_date + timedelta(seconds=random_seconds)
    
    def generate_transaction(self):
        """Generate single transaction"""
        transaction_type = random.choice(self.TRANSACTION_TYPES)
        min_amount, max_amount = self.AMOUNT_RANGES[transaction_type]
        
        transaction = {
            'transaction_id': self._generate_transaction_id(),
            'sender': self._generate_phone_number(),
            'receiver': self._generate_phone_number(),
            'amount': round(random.uniform(min_amount, max_amount), 2),
            'timestamp': self._get_random_timestamp().isoformat(),
            'transaction_type': transaction_type,
            'status': random.choices(
                self.STATUSES,
                weights=[85, 10, 3, 2]  # Weighted to favor success
            )[0],
            'provider': random.choice(self.PROVIDERS),
            'fee': round(random.uniform(0, 50), 2),
            'reference': f"REF{str(uuid.uuid4())[:8].upper()}",
        }
        return transaction
    
    def generate_transactions(self, count=1000):
        """
        Generate multiple transactions
        
        Args:
            count: Number of transactions to generate
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        for _ in range(count):
            transactions.append(self.generate_transaction())
        
        logger.info(f"Generated {count} transactions")
        return transactions
    
    def generate_and_save(self, filename, count=1000):
        """Generate transactions and save to JSON file"""
        transactions = self.generate_transactions(count)
        
        with open(filename, 'w') as f:
            json.dump(transactions, f, indent=2)
        
        logger.info(f"Saved {count} transactions to {filename}")
        return transactions

def generate_transactions(count=1000, start_date=None, end_date=None):
    """Convenience function for backward compatibility"""
    generator = TransactionGenerator(start_date, end_date)
    return generator.generate_transactions(count)

if __name__ == "__main__":
    import sys
    
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    
    generator = TransactionGenerator()
    transactions = generator.generate_transactions(count)
    
    print(f"\n✓ Generated {len(transactions)} transactions")
    print(f"\nSample transaction:")
    print(json.dumps(transactions[0], indent=2))
    
    # Save to file
    generator.generate_and_save('transactions_sample.json', count)
