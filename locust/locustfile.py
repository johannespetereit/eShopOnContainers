import sys, os, re, csv, codecs, random, json
sys.path.append(os.getcwd())
from datetime import datetime, timedelta
from locust import HttpLocust, TaskSet, task, between
from eshoptasks import TrafficTasks
from eshopexecutor import EShopExecutor


class TestTasks(TaskSet):
    def on_start(self):
        self.locust.executor.perform_login()
    @task
    def task(self):
        self.locust.executor.update_product_list_simple()
        self.locust.executor.add_to_basket()
        self.locust.executor.perform_checkout()
        self.locust.executor.show_order_detail()



def read_users(path = 'Users.csv'):
    users = []
    if not os.path.isabs(path):
        dir = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(dir, path)

    try:
        with codecs.open(path, 'r', 'utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                users.append(row)
        print(f"users loaded from @{path}")
    except FileNotFoundError:
        print(f"no users found @{path}")
        users = []
    random.shuffle(users)
    return users

users = read_users()
user_index = 0
class WebsiteUser(HttpLocust):
    def __init__(self, tasksToPerform=TrafficTasks):
        WebsiteUser.task_set = tasksToPerform
        global user_index, users
        self.user_info = None
        user_index += 1
        user_index = user_index % len(users)
        if user_index < len(users):
            print(f"setting user {str(user_index)} {users[user_index]['Email']}")
            self.user_info = users[user_index]
        else:
            print(f"too many users: {user_index}, available: {len(users)}")
            self.user_info = {'Email': 'anonymous'}

        self.executor = EShopExecutor(self)
        super().__init__()
    host = 'http://eshop.ef3cf9d0e1b34a7d845f.westeurope.aksapp.io'
    task_set = []
    # task_set = TestTasks
    wait_time = between(4, 60)
WebsiteUser.task_set = TrafficTasks

def interactive_locust(users_file = 'Users.csv'):
    global users
    if users_file != None:
        users = read_users(users_file)
    x = WebsiteUser(TrafficTasks)
    x.run()