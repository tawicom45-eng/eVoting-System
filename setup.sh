#!/bin/bash
# Setup script for entire Safaricom portfolio

set -e

echo "=========================================="
echo "Safaricom Data Engineering Portfolio Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"

# Setup Project 1
echo ""
echo "Setting up Project 1: Kenyan Market ETL..."
cd Project_1_Kenyan_Market_ETL
pip install -r requirements.txt > /dev/null 2>&1
cp .env.example .env
echo "✓ Project 1 setup complete"
cd ..

# Setup Project 2
echo ""
echo "Setting up Project 2: M-Pesa Airflow Pipeline..."
cd Project_2_MPesa_Airflow_Pipeline
pip install -r requirements.txt > /dev/null 2>&1
cp .env.example .env
echo "✓ Project 2 setup complete"
cd ..

# Setup Project 3
echo ""
echo "Setting up Project 3: Real-Time Streaming..."
cd Project_3_RealTime_Streaming
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Project 3 setup complete"
cd ..

# Setup Project 4
echo ""
echo "Setting up Project 4: Safaricom Data Warehouse..."
cd Project_4_Safaricom_DataWarehouse
pip install -r requirements.txt > /dev/null 2>&1
cp .env.example .env
echo "✓ Project 4 setup complete"
cd ..

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure .env files in each project directory"
echo "2. Ensure PostgreSQL is running"
echo "3. Create databases: kenyan_market, mpesa_db, safaricom_dw"
echo "4. Run individual projects as documented"
echo ""
echo "Documentation: COMPLETE_DOCUMENTATION.md"
echo ""
