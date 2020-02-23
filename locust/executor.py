import inspect
from datetime import datetime, timedelta
from util import guard_response

class Executor:
    def __init__(self, locust, debug = False):
        super().__init__()
        self.debug = debug
        self.locust = locust
        self.headers = {}
        self.is_logged_in = False

    def before_call(self, method):
        if self.is_logged_in:
            still_logged_in = self.login_expiration > datetime.now()
            if not still_logged_in:
                self.is_logged_in = False
                print(f"session for {self.locust.user_info['Email']} has expired")
        print(f"    {method} {inspect.stack()[2].function} for {self.locust.user_info['Email']}")

    def after_call(self, response):
        guard_response(response)
        if self.debug:
            print(f"{response.status_code}, {response.request.method}, {response.url}")


    def get(self, url, name=None):
        self.before_call('GET ')
        resp = self.locust.client.get(url, headers=self.headers, name=name)
        self.after_call(resp)
        return resp

    def post(self, url, data, headers=None):
        self.before_call('POST')
        headers = headers or {}
        for key in self.headers: headers[key] = self.headers[key]
        resp = self.locust.client.post(url, data, headers = headers)
        self.after_call(resp)
        return resp


    def json(self, url, data, headers=None):
        self.before_call('JSON')
        headers = headers or {}
        for key in self.headers: headers[key] = self.headers[key]
        resp = self.locust.client.post(url, headers = headers, json=data)
        self.after_call(resp)
        return resp

    def get_expiration_time(self, token):
        now = datetime.now()
        return now + timedelta(hours=1)
        
    def log_call(self):
        print(f"    debug: {inspect.stack()[1].function}")