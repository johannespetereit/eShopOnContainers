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
        self.locust.executor.perform_logout()
        self.locust.executor.update_product_list_simple()
        self.locust.executor.add_to_basket()
        self.locust.executor.perform_login()
        self.locust.executor.update_product_list_simple()
        self.locust.executor.add_to_basket()
        self.locust.executor.perform_logout()
        self.locust.executor.update_product_list_simple()
        self.locust.executor.add_to_basket()
        self.locust.executor.perform_login()
        self.locust.executor.perform_login()
        self.locust.executor.update_product_list_simple()
        self.locust.executor.add_to_basket()



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
user_agents = [ r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
                r"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
                r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
                r"Microsoft Internet Explorer 6 / IE 6",
                r"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
                r"Microsoft Internet Explorer 7 / IE 7",
                r"Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)",
                r"Microsoft Internet Explorer 8 / IE 8",
                r"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)",
                r"Microsoft Internet Explorer 9 / IE 9",
                r"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0;  Trident/5.0)",
                r"Microsoft Internet Explorer 10 / IE 10",
                r"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; MDDCJS)",
                r"Microsoft Internet Explorer 11 / IE 11",
                r"Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",
                r"Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
                r"Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1",
                r"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
                r"Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
                r"Mozilla/5.0 (Linux; Android 6.0.1; SAMSUNG SM-G570Y Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/4.0 Chrome/44.0.2403.133 Mobile Safari/537.36"
]


users = read_users()
class WebsiteUser(HttpLocust):
    host = 'http://eshop.5f925ea136544e4cb450.westeurope.aksapp.io'
    task_set = []
    wait_time = between(4, 60)

    def __init__(self, tasksToPerform=TrafficTasks):
        global users, user_agents
        self.user_agent_choices = user_agents
        self.user_choices = users
        WebsiteUser.task_set = tasksToPerform
        self.choose_user()
        self.executor = EShopExecutor(self)
        super().__init__()

    def choose_user(self):
        user = random.choice(self.user_choices)
        print(f"setting user {user['Email']}")
        self.user_info = user
        self.user_agent = random.choice(self.user_agent_choices)

WebsiteUser.task_set = TrafficTasks

def interactive_locust(users_file = 'Users.csv'):
    global users
    if users_file != None:
        users = read_users(users_file)
    x = WebsiteUser(TestTasks)
    x.run()