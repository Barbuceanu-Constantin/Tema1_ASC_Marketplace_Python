"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Lock
import logging
from logging.handlers import RotatingFileHandler
import time
import unittest

try:
    #For unittests
    import product as p
except ModuleNotFoundError:
    #For checker (functionality tests)
    pass

logging.basicConfig(filename="marketplace.log", level=logging.DEBUG)
LOGGER = logging.getLogger('my_logger')

FORM = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.Formatter.converter = time.gmtime
HANDLER = RotatingFileHandler('marketplace.log', mode='w', maxBytes=20 * 1024, backupCount=10)
HANDLER.setFormatter(FORM)

LOGGER.addHandler(HANDLER)
LOGGER.propagate = False

class AscMarketplace(unittest.TestCase):
    """
    Class that contains the unittests.
    """
    def setUp(self):
        """
        Method that is called each time a unittest is launched.
        It creates an instance of the marketplace and 4 possible products.
        """
        self.market = Marketplace(4)
        self.product1 = p.Tea("Herbal", "GREEN", 5)
        self.product2 = p.Coffee("Brasil", 5.05, "MEDIUM", 15)
        self.product3 = p.Tea("WildCherry", "RED", 7)
        self.product4 = p.Coffee("Indonesia", 6.01, "HIGH", 20)

    def test_register_producer(self):
        """
        Unittest that tests register_producer method.
        """
        self.assertEqual(self.market.producer_id + 1, self.market.register_producer())
        self.assertEqual(self.market.nr_products_dictionary[self.market.producer_id], 0)

    def test_publish(self):
        """
        Unittest that tests publish method.
        """
        self.market.register_producer()
        self.market.register_producer()
        self.assertTrue(self.market.publish(1, self.product1))
        self.assertTrue(self.market.publish(1, self.product2))
        self.assertTrue(self.market.publish(1, self.product3))
        self.assertTrue(self.market.publish(2, self.product4))
        self.assertTrue(self.market.publish(1, self.product1))
        self.assertFalse(self.market.publish(1, self.product1))

    def test_new_cart(self):
        """
        Unittest that tests new_cart method.
        """
        self.assertEqual(self.market.cart_id + 1, self.market.new_cart())
        self.assertFalse(self.market.carts_dictionary[self.market.cart_id])

    def test_add_to_cart(self):
        """
        Unittest that tests add_to_cart method.
        """
        self.market.new_cart()
        self.market.new_cart()
        self.market.register_producer()
        self.market.register_producer()
        self.market.publish(1, self.product1)
        self.market.publish(1, self.product2)
        self.market.publish(1, self.product3)
        self.market.publish(2, self.product4)
        self.assertTrue(self.market.add_to_cart(1, self.product1))
        self.assertFalse(self.market.add_to_cart(1, self.product1))
        self.assertTrue(self.market.add_to_cart(2, self.product4))
        self.assertFalse(self.market.add_to_cart(2, self.product4))
        self.assertIn((1, self.product1), self.market.carts_dictionary[1])
        self.assertIn((2, self.product4), self.market.carts_dictionary[2])
        self.assertNotIn((1, self.product1), self.market.list_of_products)
        self.assertNotIn((2, self.product4), self.market.list_of_products)

    def test_remove_from_cart(self):
        """
        Unittest that tests remove_from_cart method.
        """
        self.market.new_cart()
        self.market.new_cart()
        self.market.register_producer()
        self.market.register_producer()
        self.market.publish(1, self.product1)
        self.market.publish(1, self.product2)
        self.market.publish(1, self.product3)
        self.market.publish(2, self.product4)
        self.market.add_to_cart(1, self.product1)
        self.market.add_to_cart(1, self.product2)
        self.market.add_to_cart(2, self.product3)
        self.market.add_to_cart(2, self.product4)
        self.market.remove_from_cart(1, self.product1)
        self.market.remove_from_cart(2, self.product4)
        self.assertIn((1, self.product1), self.market.list_of_products)
        self.assertIn((2, self.product4), self.market.list_of_products)
        self.assertNotIn((1, self.product1), self.market.carts_dictionary[1])
        self.assertNotIn((2, self.product4), self.market.carts_dictionary[2])

    def test_place_order(self):
        """
        Unittest that tests place_order method.
        """
        self.market.new_cart()
        self.market.register_producer()
        self.market.register_producer()
        self.market.publish(1, self.product1)
        self.market.publish(1, self.product2)
        self.market.publish(1, self.product3)
        self.market.publish(2, self.product4)
        self.market.add_to_cart(1, self.product1)
        self.market.add_to_cart(1, self.product2)
        self.assertIn(self.product1, self.market.place_order(1))
        self.assertFalse(self.market.carts_dictionary[1])
        self.market.add_to_cart(1, self.product3)
        self.assertIn(self.product3, self.market.place_order(1))
        self.assertFalse(self.market.carts_dictionary[1])

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        LOGGER.info("=============================")
        LOGGER.info("__init__ : ")
        LOGGER.info(str(queue_size_per_producer))
        LOGGER.info("=============================")

        self.queue_size_per_producer = queue_size_per_producer
        self.producer_id_lock = Lock()
        self.cart_id_lock = Lock()
        self.remove_lock = Lock()
        self.producer_id = 0
        self.cart_id = 0
        self.nr_products_dictionary = {}
        self.carts_dictionary = {}
        self.list_of_products = []

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        LOGGER.info("register_producer in")
        LOGGER.info("register_producer out")

        with self.producer_id_lock:
            self.producer_id = self.producer_id + 1
            self.nr_products_dictionary[self.producer_id] = 0

        return self.producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        LOGGER.info("publish in : ")
        LOGGER.info("producer_id = %s", str(producer_id))
        LOGGER.info("product = %s", str(product))
        LOGGER.info("publish out")

        if self.nr_products_dictionary[producer_id] < self.queue_size_per_producer:
            self.nr_products_dictionary[producer_id] = self.nr_products_dictionary[producer_id] + 1
            self.list_of_products.append((producer_id, product))
            return True

        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        LOGGER.info("new_cart in")
        LOGGER.info("new_cart out")

        with self.cart_id_lock:
            self.cart_id = self.cart_id + 1
            self.carts_dictionary[self.cart_id] = []

        return self.cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        LOGGER.info("add_to_cart in : ")
        LOGGER.info("cart_id = %s", str(cart_id))
        LOGGER.info("product = %s", str(product))
        LOGGER.info("add_to_cart out")

        #Check if product exists in list_of_products.
        for elem in self.list_of_products:
            #If it is there:
            if elem[1] == product:
                #Many consumers may try tor remove the same element
                #at the same time. That is the reason for remove_lock.
                self.remove_lock.acquire()

                #If the product has been already taken.
                if self.list_of_products.count(elem) == 0:
                    self.remove_lock.release()
                    continue

                #Add the product in the cart list of products.
                #elem <=> (producer_id, product)
                self.carts_dictionary[cart_id].append((elem[0], product))

                #Eliminate the product from the available list of products.
                self.list_of_products.remove(elem)

                self.remove_lock.release()

                return True

        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        LOGGER.info("remove_from_cart in : ")
        LOGGER.info("cart_id = %s", str(cart_id))
        LOGGER.info("product = %s", str(product))
        LOGGER.info("remove_from_cart out")

        cart_list = self.carts_dictionary[cart_id]

        for cart_product in cart_list:
            if cart_product[1] == product:
                #Eliminate the product from the cart_list.
                cart_list = cart_list.remove(cart_product)

                #Readd the product in the global list of products.
                self.list_of_products.append(cart_product)

                return

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        LOGGER.info("place_order in : ")
        LOGGER.info("cart_id = %s", str(cart_id))
        LOGGER.info("place_order out")

        cart_list = self.carts_dictionary[cart_id]

        #Once the order is placed each number of products of the
        #corresponding producer have to be decremented accordingly.
        for cart_p in cart_list:
            self.nr_products_dictionary[cart_p[0]] = self.nr_products_dictionary[cart_p[0]] - 1

        #Create the list of products.
        new_l = []
        for elem_pair in cart_list:
            new_l.append(elem_pair[1])

        #Make the cart list empty.
        self.carts_dictionary[cart_id] = []

        #Return the list of products.
        return new_l
