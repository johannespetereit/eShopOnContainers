from locust import TaskSet, task, seq_task

class TrafficTasks(TaskSet):
    def on_start(self):
        pass

    @task(70)
    class Browse(TaskSet):
        def on_start(self):
            print(self.locust.user_info["Email"], "is browsing")
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
                print(self.locust.user_info["Email"], "cannot shop, not logged in")
                self.interrupt()
            else:
                print(self.locust.user_info["Email"], "starts shopping")
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
        @task(13)
        def show_orders(self):
            self.locust.executor.show_orders()
        @task(12)
        def show_order_detail(self):
            self.locust.executor.show_order_detail()
        @task(10)
        def goto_checkout(self):
            self.locust.executor.show_checkout()
    
    @task(30)
    class Checkout(TaskSet):
        def on_start(self):
            if not self.locust.executor.is_logged_in or not self.locust.executor.has_items_in_basket:
                print(self.locust.user_info["Email"], "can't checkout, not logged in or nothing in basket")
                self.interrupt()
            else:
                print(self.locust.user_info["Email"], "checking out")
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
                print(self.locust.user_info["Email"], "cannot login: No user available to login")
                self.interrupt()
            elif self.locust.executor.is_logged_in:
                print(self.locust.user_info["Email"], "is already logged in")
                self.interrupt()
            else:
                print(self.locust.user_info["Email"], "is logging in")
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