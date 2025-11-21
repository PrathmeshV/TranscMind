from locust import HttpUser, task, between
import random

class APITestUser(HttpUser):
    wait_time = between(0.001, 0.005)

    @task
    def predict(self):
        samples = [
            "Walmart Supercenter 1234",
            "Netflix subscription",
            "Unknown POS 9999",
            "Delta Airlines ticket"
        ]
        text = random.choice(samples)
        self.client.post('/predict', json={'transaction_text': text})
