from locust import HttpUser, task

class QuickStartUser(HttpUser):
    
    def on_start(self):
        response = self.client.post('/auth/login', json={
            "username": "aron",
            "password": "aaaaa",
        })
        access_token = response.json()['access']
        self.client.headers = {"Authorization": f"Bearer {access_token}"}
    
    @task
    def test_hi(self):
        self.client.get('/test-locale/hi')
        
    @task
    def test_bye(self):
        self.client.get('/test-locale/bye')
        
    @task
    def test_maktabkhooneh(self):
        self.client.get('/test-locale/maktabkhooneh')
        
    @task
    def get_expense(self):
        self.client.get('/expense/')
    