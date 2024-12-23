"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time

class Producer(Thread):
    """
    Class that represents a producer.
     """
    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        super().__init__(**kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.kwargs = kwargs

    def run(self):
        #The producer is assigned an id.
        producer_id = self.marketplace.register_producer()

        #The producers product in continuos mode.
        while True:
            for product in self.products:
                quantity = product[1]               #Quantity
                producing_time = product[2]         #Producing time

                #I go through each element in the given quantity.
                for _ in range(quantity):

                    #While the producer can`t add another product(presumption).
                    can_add_product = False
                    while not can_add_product:
                        time.sleep(producing_time)
                        can_add_product = self.marketplace.publish(producer_id, product[0])

                        if not can_add_product:
                            #Se asteapta timpul de republicare
                            time.sleep(self.republish_wait_time)
