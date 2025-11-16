"""
M-Pesa ETL Apache Airflow DAG

Orchestrates the M-Pesa transaction ETL pipeline with Airflow.
Handles data extraction, validation, cleaning, and loading.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
import logging

logger = logging.getLogger(__name__)

# Default arguments for DAG
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'email': ['data-team@company.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=1),
}

# DAG definition
dag = DAG(
    'mpesa_etl_pipeline',
    default_args=default_args,
    description='M-Pesa transaction ETL pipeline with quality checks',
    schedule_interval='0 */6 * * *',  # Every 6 hours
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['mpesa', 'etl', 'transactions'],
)

# ===== Python Callables =====

def extract_transactions(**context):
    """Extract transaction data from source systems"""
    from generator.transaction_generator import TransactionGenerator
    
    logger.info("Starting transaction extraction...")
    
    generator = TransactionGenerator()
    transactions = generator.generate_transactions(count=5000)
    
    # Push to XCom for downstream tasks
    context['task_instance'].xcom_push(key='transaction_count', value=len(transactions))
    context['task_instance'].xcom_push(key='transactions', value=transactions)
    
    logger.info(f"Extracted {len(transactions)} transactions")
    return len(transactions)

def validate_raw_data(**context):
    """Validate raw extracted data"""
    logger.info("Validating raw data...")
    
    ti = context['task_instance']
    transactions = ti.xcom_pull(task_ids='extract_transactions', key='transactions')
    
    if not transactions:
        raise ValueError("No transactions extracted")
    
    # Data validation checks
    validation_results = {
        'total_records': len(transactions),
        'required_fields': ['transaction_id', 'sender', 'receiver', 'amount'],
        'valid_records': 0,
        'invalid_records': 0
    }
    
    for txn in transactions:
        has_required = all(field in txn for field in validation_results['required_fields'])
        if has_required and txn.get('amount', 0) > 0:
            validation_results['valid_records'] += 1
        else:
            validation_results['invalid_records'] += 1
    
    validation_rate = (validation_results['valid_records'] / validation_results['total_records']) * 100
    logger.info(f"Validation rate: {validation_rate:.2f}%")
    
    if validation_rate < 95:
        raise ValueError(f"Data validation failed. Valid rate: {validation_rate:.2f}%")
    
    ti.xcom_push(key='validation_results', value=validation_results)
    return validation_results

def clean_data(**context):
    """Clean and standardize transaction data"""
    logger.info("Cleaning transaction data...")
    
    ti = context['task_instance']
    transactions = ti.xcom_pull(task_ids='extract_transactions', key='transactions')
    
    cleaned_transactions = []
    for txn in transactions:
        cleaned_txn = {
            'transaction_id': str(txn.get('transaction_id', '')).strip(),
            'sender': str(txn.get('sender', '')).strip(),
            'receiver': str(txn.get('receiver', '')).strip(),
            'amount': float(txn.get('amount', 0)),
            'timestamp': txn.get('timestamp', datetime.now().isoformat()),
            'transaction_type': str(txn.get('transaction_type', 'unknown')).lower(),
            'status': str(txn.get('status', 'pending')).lower(),
            'provider': str(txn.get('provider', 'unknown')).strip(),
            'fee': float(txn.get('fee', 0)),
            'net_amount': float(txn.get('amount', 0)) - float(txn.get('fee', 0)),
        }
        cleaned_transactions.append(cleaned_txn)
    
    logger.info(f"Cleaned {len(cleaned_transactions)} transactions")
    ti.xcom_push(key='cleaned_transactions', value=cleaned_transactions)
    return len(cleaned_transactions)

def detect_fraud(**context):
    """Apply fraud detection rules"""
    logger.info("Running fraud detection...")
    
    ti = context['task_instance']
    transactions = ti.xcom_pull(task_ids='clean_data', key='cleaned_transactions')
    
    fraud_indicators = {
        'total_transactions': len(transactions),
        'flagged_suspicious': 0,
        'high_value_txns': 0,
        'rapid_transactions': 0,
    }
    
    # Rule 1: Flag high-value transactions
    for txn in transactions:
        if txn['amount'] > 50000:
            fraud_indicators['high_value_txns'] += 1
            txn['risk_level'] = 'high'
        elif txn['amount'] > 10000:
            fraud_indicators['rapid_transactions'] += 1
            txn['risk_level'] = 'medium'
        else:
            txn['risk_level'] = 'low'
    
    # Rule 2: Flag failed transactions
    for txn in transactions:
        if txn['status'] == 'failed':
            fraud_indicators['flagged_suspicious'] += 1
    
    fraud_rate = (fraud_indicators['flagged_suspicious'] / fraud_indicators['total_transactions']) * 100
    logger.info(f"Fraud detection complete. Flagged: {fraud_rate:.2f}%")
    
    ti.xcom_push(key='fraud_results', value=fraud_indicators)
    ti.xcom_push(key='transactions_with_risk', value=transactions)
    return fraud_indicators

def load_to_database(**context):
    """Load cleaned and validated data to database"""
    logger.info("Loading data to database...")
    
    ti = context['task_instance']
    transactions = ti.xcom_pull(task_ids='detect_fraud', key='transactions_with_risk')
    
    # Simulated database insertion
    load_stats = {
        'total_inserted': len(transactions),
        'successful': len([t for t in transactions if t['status'] == 'success']),
        'failed': len([t for t in transactions if t['status'] == 'failed']),
        'pending': len([t for t in transactions if t['status'] == 'pending']),
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"Loaded {load_stats['total_inserted']} transactions to database")
    logger.info(f"  - Successful: {load_stats['successful']}")
    logger.info(f"  - Failed: {load_stats['failed']}")
    logger.info(f"  - Pending: {load_stats['pending']}")
    
    ti.xcom_push(key='load_stats', value=load_stats)
    return load_stats

def generate_report(**context):
    """Generate ETL execution report"""
    logger.info("Generating ETL report...")
    
    ti = context['task_instance']
    extraction_count = ti.xcom_pull(task_ids='extract_transactions', key='transaction_count')
    validation_results = ti.xcom_pull(task_ids='validate_raw_data', key='validation_results')
    fraud_results = ti.xcom_pull(task_ids='detect_fraud', key='fraud_results')
    load_stats = ti.xcom_pull(task_ids='load_to_database', key='load_stats')
    
    report = {
        'dag_execution_date': context['execution_date'].isoformat(),
        'extraction': {
            'total_transactions': extraction_count,
        },
        'validation': validation_results,
        'fraud_detection': fraud_results,
        'loading': load_stats,
        'pipeline_status': 'SUCCESS',
        'completed_at': datetime.now().isoformat()
    }
    
    logger.info("="*60)
    logger.info("ETL PIPELINE EXECUTION REPORT")
    logger.info("="*60)
    logger.info(f"Extracted: {extraction_count} transactions")
    logger.info(f"Valid: {validation_results['valid_records']}")
    logger.info(f"Loaded: {load_stats['total_inserted']}")
    logger.info(f"Status: {report['pipeline_status']}")
    logger.info("="*60)
    
    return report

# ===== DAG Tasks =====

with dag:
    
    # Extract Phase
    extract_task = PythonOperator(
        task_id='extract_transactions',
        python_callable=extract_transactions,
        provide_context=True,
        retries=1,
    )
    
    # Validation Phase
    with TaskGroup('validation_group', tooltip='Data validation tasks') as validation_group:
        validate_task = PythonOperator(
            task_id='validate_raw_data',
            python_callable=validate_raw_data,
            provide_context=True,
        )
    
    # Transformation Phase
    with TaskGroup('transformation_group', tooltip='Data cleaning and enrichment') as transformation_group:
        clean_task = PythonOperator(
            task_id='clean_data',
            python_callable=clean_data,
            provide_context=True,
        )
        
        fraud_task = PythonOperator(
            task_id='detect_fraud',
            python_callable=detect_fraud,
            provide_context=True,
        )
    
    # Loading Phase
    load_task = PythonOperator(
        task_id='load_to_database',
        python_callable=load_to_database,
        provide_context=True,
        retries=1,
    )
    
    # Reporting
    report_task = PythonOperator(
        task_id='generate_report',
        python_callable=generate_report,
        provide_context=True,
    )
    
    # Task Dependencies
    extract_task >> validation_group >> transformation_group >> load_task >> report_task
