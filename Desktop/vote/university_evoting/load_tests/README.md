Run with Locust:

1. Install locust: pip install locust
2. Start the app locally (e.g., manage.py runserver)
3. Run: locust -f load_tests/locustfile.py --host=http://localhost:8000

The script is a simple starting point and should be extended to handle real authentication and realistic voting flows.