from locust import HttpUser, TaskSet, task
from locust.user import task


class UserBehave(TaskSet):
    @task
    def login(self):
        resp = self.client.get("https://remotedesk.ue")

class WebUser(HttpUser):
    task_set = UserBehave
    max_wait = 5000
    min_wait = 1000