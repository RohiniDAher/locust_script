from foo_app import FooApplication
from locust import TaskSet, task


class FooTaskSet(TaskSet):
    def on_start(self):
        self.foo = FooApplication(self.client)

    @task(1)
    def login(self):
        if not self.foo.is_logged_in:
            self.foo.login()
