import sys, os, re, csv, codecs, random, json
from datetime import datetime
from locust import HttpLocust, TaskSet, task, between, seq_task
from urllib.parse import quote
import urllib.parse as urlparse
from urllib.parse import parse_qs
from util import dump, guard_response
from auth import oauth_login
import inspect
dir = os.path.dirname(os.path.realpath(__file__))
user_file_path = os.path.join(dir, 'Users.csv')

class Executor:
    def __init__(self, locust, debug = False):
        super().__init__()
        self.can_log_in = locust.user_info != None
        self.debug = debug
        self.locust = locust
        self.headers = {}
        self.auth = None
        self.is_logged_in = False
        self.has_items_in_basket = False
        self.has_orders = False
        # baskets are called by id
        self.basket_id = None
        self.last_displayed_products = []

    def get(self, url, name=None):
        self.client = self.locust.client
        print("    get:  ", inspect.stack()[1].function)
        resp = self.client.get(url, headers=self.headers, name=name)
        guard_response(resp)
        if self.debug:
            print(resp.status_code, resp.request.method, resp.url)
        return resp
    def post(self, url, data, headers=None):
        self.client = self.locust.client
        print("    post: ", inspect.stack()[1].function)
        headers = headers or {}
        for key in self.headers: headers[key] = self.headers[key]
        resp = self.client.post(url, data, headers = headers)
        guard_response(resp)
        if self.debug:
            print(resp.status_code, resp.request.method, resp.url)
        return resp
    def json(self, url, data, headers=None):
        self.client = self.locust.client
        print("    post: ", inspect.stack()[1].function)
        headers = headers or {}
        for key in self.headers: headers[key] = self.headers[key]
        resp = self.client.post(url, headers = headers, json=data)
        guard_response(resp)
        if self.debug:
            print(resp.status_code, resp.request.method, resp.url)
        return resp

    def log_call(self):
        self.client = self.locust.client
        print("    debug:" + inspect.stack()[1].function)

    def show_index(self):
        self.get("/")
        if (self.auth):
            self.get("/webshoppingapigw/c/api/v1/catalog/catalogbrands")
            self.get("/webshoppingapigw/c/api/v1/catalog/catalogtypes")
    def update_product_list_simple(self):
        page = str(random.randint(0,1))
        resp = self.get("/webshoppingapigw/c/api/v1/catalog/items?pageIndex=" + page + "&pageSize=10", name='/webshoppingapigw/c/api/v1/catalog/items?pageIndex=[page]')
        self.last_displayed_products = json.loads(resp.text)["data"]
    def update_product_list(self):
        
        # prod_brand = "[1-4, null, all?, EMPTY?]"
        # prod_type = "[1-4, null, all?, EMPTY?]"
        prod_brand = str(random.randint(1,4))
        prod_type = str(random.randint(1,4))
        resp = self.get("/webshoppingapigw/c/api/v1/catalog/items/type/" + prod_type + "/brand/" + prod_brand + "?pageIndex=0&pageSize=10", name='/webshoppingapigw/c/api/v1/catalog/items/type/[type]/brand/[brand]?pageIndex=0&pageSize=10')
        self.last_displayed_products = json.loads(resp.text)["data"]
    def show_login(self):
        self.get("/identity/Account/Login")
    def perform_login(self):
        self.log_call()
        if (self.is_logged_in): return
        username = self.locust.user_info["Email"]
        password = self.locust.user_info["Password"]
        self.access_token = oauth_login(self.client, username, password)
        self.auth = 'Bearer ' + self.access_token
        self.headers = {'Authorization': self.auth}
        self.is_logged_in = True
        # these calls always happen after login
        resp = self.get("/identity/connect/userinfo")
        self.basket_id = json.loads(resp.text)["sub"]
        self.get("/Home/Configuration")
    def give_up_login(self):
        self.show_index()
    def show_register(self):
        self.get("/identity/Account/Register")
    def perform_register(self):
        self.log_call()
        # self.get("test")
        pass
    def give_up_register(self):
        self.show_index()
    def add_to_basket(self):
        available_count = len(self.last_displayed_products)-1
        if available_count < 1: return
        random.shuffle(self.last_displayed_products)
        take = random.randint(1,available_count)
        toAdd = self.last_displayed_products[0:take]
        items = [{
                    "pictureUrl": e["pictureUri"],
                    "productId": e["id"],
                    "productName": e["name"],
                    "quantity": 1,
                    "unitPrice": e["price"],
                    "id": "f157d53d-60f8-4a2f-8a57-2be3ab8a06ee",
                    "oldUnitPrice": 0
                } for e in toAdd]
        resp = self.json('/webshoppingapigw/api/v1/basket/', data={
            "buyerId": self.basket_id,
            "items": items
        }, headers={'Content-Type': 'application/json'})
    def show_basket(self):
        self.get("/basket")
        resp = self.get('/webshoppingapigw/b/api/v1/basket/' + self.basket_id, name='/webshoppingapigw/b/api/v1/basket')
        self.has_items_in_basket = len(json.loads(resp.text)["items"]) != 0
    def show_checkout(self):
        self.get("/order")
        self.show_basket()
    def perform_checkout(self):
        resp = self.post("/order/", {
            "street": "8957 Karianne Square",
            "city": "New Alena",
            "country": "Hong Kong",
            "state": "ND",
            "zipcode": "06076",
            "cardexpiration": "2020-10-31T23:00:00.000Z",
            "cardnumber": "3441-119728-68939",
            "cardsecuritynumber": "452",
            "cardtypeid": 1,
            "cardholdername": "Alf Torphy",
            "total": 0,
            "expiration": "10/20"
        })
    def show_orders(self):
        self.get("/orders")
        resp = self.get("/webshoppingapigw/o/api/v1/orders")
        self.has_orders = len(json.loads(resp.text)) != 0
    def show_order_detail(self):
        resp = self.get("/webshoppingapigw/o/api/v1/orders")
        orders = json.loads(resp.text)
        if len(orders) == 0: return
        random.shuffle(orders)
        resp = self.get("/webshoppingapigw/o/api/v1/orders/" + str(orders[0]["ordernumber"]))

# ================================================================================================================
# ================================================================================================================
# ================================================================================================================
# ================================================================================================================

class TestTasks(TaskSet):
    def on_start(self):
        self.locust.executor.perform_login()
        self.locust.executor.show_order_detail()
        # self.locust.executor.add_to_basket()
    @task
    def none(self):
        self.interrupt()

# ================================================================================================================
# ================================================================================================================
# ================================================================================================================
# ================================================================================================================




class WebsiteTasks(TaskSet):
    def on_start(self):
        pass

    @task(70)
    class Browse(TaskSet):
        def on_start(self):
            print("start browsing")
            self.reload_shop()
        
        @task(15)
        def reload_shop(self):
            self.locust.executor.show_index()

        @task(30)
        def update_product_list(self):
            self.locust.executor.update_product_list()
        @task(80)
        def update_product_list_simple(self):
            self.locust.executor.update_product_list_simple()

        @task(7)
        def stop_browsing(self):
            self.interrupt()

            
    @task(50)
    class Shop(TaskSet):
        def on_start(self):
            if not self.locust.executor.is_logged_in:
                print("cannot shop, not logged in")
                self.interrupt()
            else:
                print("start shopping")
        @task(20)
        def add_to_basket(self):
            self.locust.executor.add_to_basket()
        @task(30)
        def reload_shop(self):
            self.locust.executor.show_index()
        @task(30)
        def update_product_list(self):
            self.locust.executor.update_product_list()
        @task(80)
        def update_product_list_simple(self):
            self.locust.executor.update_product_list_simple()
        @task(40)
        def stop_shopping(self):
            self.interrupt()
        @task(20)
        def show_basket(self):
            self.locust.executor.show_basket()
    
    @task(30)
    class Checkout(TaskSet):
        def on_start(self):
            if not self.locust.executor.is_logged_in or not self.locust.executor.has_items_in_basket:
                print("can't checkout, not logged in")
                self.interrupt()
            else:
                print("checking out")
        @seq_task(1)
        def show_basket(self):
            self.locust.executor.show_basket()
        @seq_task(2)
        def goto_checkout(self):
            self.locust.executor.show_checkout()
        @seq_task(3)
        def perform_checkout(self):
            self.locust.executor.perform_checkout()
            self.interrupt()

    @task(40)
    class Login(TaskSet):
        def on_start(self):
            if not self.locust.executor.can_log_in:
                print("no user available to login")
                self.interrupt()
            elif self.locust.executor.is_logged_in:
                print("already logged in")
                self.interrupt()
            else:
                print("logging in")
                self.show_login()
        
        def show_login(self):
            self.locust.executor.show_login()
        
        @task(80)
        def perform_login(self):
            self.locust.executor.perform_login()
            self.interrupt()
            
        @task(12)
        def give_up_login(self):
            self.locust.executor.give_up_login()
            self.interrupt()

        @task(10)
        class Register(TaskSet):
            def on_start(self):
                self.show_register()
            def show_register(self):
                self.locust.executor.show_register()
            @task(30)
            def perform_register(self):
                self.locust.executor.perform_register()
                self.interrupt()
            @task(70)
            def give_up_register(self):
                self.locust.executor.give_up_register()
                self.interrupt()

users = []
with codecs.open(user_file_path, 'r', 'utf-16-le') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        users.append(row)

random.shuffle(users)
user_index = 0
class WebsiteUser(HttpLocust):
    def __init__(self):
        global user_index, users
        self.user_info = None
        user_index += 1
        if user_index < len(users):
            print("setting user", str(user_index), users[user_index]["Email"])
            self.user_info = users[user_index]
        else:
            print("too many users", str(user_index), ", available:", len(users))

        self.executor = Executor(self)
        super().__init__()
    host = 'http://eshop.f3b079f4a4a5435b87e9.westeurope.aksapp.io'
    task_set = WebsiteTasks
    # task_set = TestTasks
    wait_time = between(4, 12)

if len(sys.argv) > 1 and sys.argv[1] == '-i':
    x = WebsiteUser()
    x.run()

