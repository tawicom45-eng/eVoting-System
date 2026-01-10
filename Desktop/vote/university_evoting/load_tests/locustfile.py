from locust import HttpUser, task, between
import random

class VotingUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # simple account creation is out of scope; assume user exists and credentials configured via environment
        self.identifier = 'loaduser'
        self.password = 'password'

    @task(3)
    def login_and_refresh(self):
        r = self.client.post('/api/auth/login/', json={'identifier': self.identifier, 'password': self.password})
        if r.status_code == 200:
            refresh = r.json().get('refresh_token')
            # refresh once
            self.client.post('/api/auth/refresh/', json={'refresh_token': refresh})

    @task(7)
    def cast_vote(self):
        # simplified: assume access token issued and can be set via header
        # in a real scenario, store and refresh access tokens per user
        self.client.post('/api/vote/cast/', json={'choice': random.randint(1, 10)})
