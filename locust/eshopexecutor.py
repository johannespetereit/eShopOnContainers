import random, uuid
from auth import oauth_login
from executor import Executor
import json

class EShopExecutor(Executor):
    def __init__(self, locust, debug = False):
        super().__init__(locust, debug)
        self.auth = None
        self.has_items_in_basket = False
        self.has_orders = False
        # baskets are called by id
        self.basket_id = None
        self.last_displayed_products = []
        self.can_log_in = self.locust.user_info != None and 'Password' in self.locust.user_info

    def show_index(self):
        self.get("/")
        if self.is_logged_in:
            self.get("/webshoppingapigw/c/api/v1/catalog/catalogbrands")
            self.get("/webshoppingapigw/c/api/v1/catalog/catalogtypes")

    def update_product_list_simple(self):
        page = str(random.randint(0,1))
        resp = self.get("/webshoppingapigw/c/api/v1/catalog/items?pageIndex=" + page + "&pageSize=10", name='/webshoppingapigw/c/api/v1/catalog/items?pageIndex=[page]')
        if resp.ok:
            self.last_displayed_products = json.loads(resp.text)["data"]

    def update_product_list(self):
        prod_brand = str(random.randint(1,4))
        prod_type = str(random.randint(1,4))
        resp = self.get("/webshoppingapigw/c/api/v1/catalog/items/type/" + prod_type + "/brand/" + prod_brand + "?pageIndex=0&pageSize=10", name='/webshoppingapigw/c/api/v1/catalog/items/type/[type]/brand/[brand]?pageIndex=0&pageSize=10')
        if resp.ok:
            self.last_displayed_products = json.loads(resp.text)["data"]

    def show_login(self):
        self.get("/identity/Account/Login")

    def perform_login(self):
        if self.is_logged_in or not self.can_log_in: return
        username = self.locust.user_info['Email']
        password = self.locust.user_info["Password"]
        self.access_token = oauth_login(self.locust.client, username, password)
        if self.access_token != None:
            self.auth = 'Bearer ' + self.access_token
            self.headers = {'Authorization': self.auth}
            self.is_logged_in = True
            self.login_expiration = self.get_expiration_time(self.access_token)
            # these calls always happen after login
            resp = self.get("/identity/connect/userinfo")
            if resp.ok:
                self.basket_id = json.loads(resp.text)["sub"]
                self.get("/Home/Configuration")
        else: 
            self.show_index()

    def give_up_login(self):
        self.show_index()

    def show_register(self):
        self.get("/identity/Account/Register")

    def perform_register(self):
        self.log_call()
        pass

    def give_up_register(self):
        self.show_index()
    
    def add_to_basket(self):
        available_count = len(self.last_displayed_products)-1
        if available_count < 1: 
            print("cannot add something to cart, as no results are visible")
            return
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
        if resp.ok:
            self.has_items_in_basket = len(json.loads(resp.text)["items"]) != 0
    
    def show_checkout(self):
        self.get("/order")
        self.show_basket()
    def perform_checkout(self):
        if not self.is_logged_in: return
        user = self.locust.user_info
        resp = self.json("/webshoppingapigw/b/api/v1/basket/checkout", {
            "street": user["Street"],
            "city": user["City"],
            "country": user["Country"],
            "state": user["State"],
            "zipcode": user["ZipCode"],
            "cardexpiration": "2022-10-31T23:00:00.000Z",
            "cardnumber": user["CardNumber"],
            "cardsecuritynumber": user["SecurityNumber"],
            "cardtypeid": user["CardType"],
            "cardholdername": user["CardHolderName"],
            "total": 0,
            "expiration": user["Expiration"]
        }, headers={'x-requestid': str(uuid.uuid4())})
        if resp.ok:
            self.show_orders()
    
    def show_orders(self):
        self.get("/orders")
        resp = self.get("/webshoppingapigw/o/api/v1/orders")
        if resp.ok:
            self.has_orders = len(json.loads(resp.text)) != 0
    
    def show_order_detail(self):
        resp = self.get("/webshoppingapigw/o/api/v1/orders")
        if resp.ok:
            orders = json.loads(resp.text)
            if len(orders) == 0: return
            random.shuffle(orders)
            resp = self.get("/webshoppingapigw/o/api/v1/orders/" + str(orders[0]["ordernumber"]))
