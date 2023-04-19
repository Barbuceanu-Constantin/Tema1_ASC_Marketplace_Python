"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread, Lock
import time
import sys

class Consumer(Thread):
    """
    Class that represents a consumer.
    """
    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        super().__init__(**kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.kwargs = kwargs
        self.print_lock = Lock()

    def run(self):
        #The consumer is assigned a cart_id.
        cart_id = self.marketplace.new_cart()

        for cart in self.carts:
            for operation in cart:
                quantity = operation["quantity"]

                if operation["type"] == "add":
                    for _ in range(quantity):
                        #I suppose the searched product is not available.
                        ret = False

                        while not ret:
                            #While it is not available I try to add it to the cart.
                            ret = self.marketplace.add_to_cart(cart_id, operation["product"])

                            if not ret:
                                time.sleep(self.retry_wait_time)

                elif operation["type"] == "remove":
                    #Eliminate the products from the cart.
                    for _ in range(quantity):
                        self.marketplace.remove_from_cart(cart_id, operation["product"])

            product_list = self.marketplace.place_order(cart_id)

            #Print the bought products.
            for product in product_list:
                with self.print_lock:
                    print(str(self.kwargs["name"]) + " bought " + str(product))
                    sys.stdout.flush()
