from django.db import models

from order_service_v2.errors import UnauthorizedError
from orders.models import Order
from .base_api_test import WrapperForBaseTestClass


class OrderEndpointTests(WrapperForBaseTestClass.BaseEndpointsTests):
    """Test goods list endpoint.
        """
    model = Order
    mutation_create = '''mutation{{
          createOrder(timeOfOrder:"1999-05-23 11:12",
             deliveryAddress:"{0}",
             goodsIds: [1, 2]
             ){{
            id
            timeOfOrder
            deliveryAddress
            itemsPrice
            deliveryPrice
            user{{
              id
            }}
          }}
        }}'''
    mutation_create_name = "createOrder"
    all_query = """query{
                  orders{
                    id
                    timeOfOrder
                    deliveryAddress
                    itemsPrice
                    deliveryPrice
                    deliveryStatus
                    paymentStatus
                    user{
                      id
                      username
                    }               
                  }
                }"""
    by_id_query = """query{
                  orders(searchedId:2){
                    id
                    timeOfOrder
                    deliveryAddress
                    itemsPrice
                    deliveryPrice
                    deliveryStatus
                    paymentStatus
                    user{
                      id
                      username
                    }
                  }
                }"""
    mutation_update = '''mutation{{
                          updateOrder(
                            orderId:{0},
                            deliveryAddress:"{1}",
                          ){{
                            id
                            timeOfOrder
                            deliveryAddress
                            itemsPrice
                            deliveryPrice
                            deliveryStatus
                            paymentStatus
                            user{{
                              id
                              username
                            }}
                          }}
                        }}'''
    mutation_update_name = 'updateOrder'

    mutation_delete = '''mutation{{
                          deleteOrder(orderId:{0}){{
                            id
                          }}
                        }}'''
    plural_name = "orders"

    @staticmethod
    def create_item_with(user) -> models.Model:
        item = Order(time_of_order="1999-05-23 11:12",
                     user_id=user.id,
                     delivery_address="asdasd",
                     delivery_status="created",
                     delivery_price=123,
                     items_price=145,
                     payment_status="not paid")
        item.save()
        return item

    def test_create_item_as_admin(self):
        self.create_item_as("admin")

    def test_create_item_as_seller(self):
        with self.assertRaises(UnauthorizedError):
            self.create_item_as("seller")

    def test_create_item_as_user(self):
        self.create_item_as("user")

    def test_create_item_as_anon(self):
        with self.assertRaises(UnauthorizedError):
            self.create_item_as()

    def test_update_by_id_as_admin(self):
        self.update_by_id_as(role="admin", fields=["deliveryAddress"])

    def test_update_by_id_as_seller(self):
        with self.assertRaises(UnauthorizedError):
            self.update_by_id_as(role="seller", fields=["deliveryAddress"])

    def test_update_by_id_as_user(self):
        with self.assertRaises(UnauthorizedError):
            self.update_by_id_as(role="user", fields=["deliveryAddress"])

    def test_update_by_id_as_anon(self):
        with self.assertRaises(UnauthorizedError):
            self.update_by_id_as(fields=["deliveryAddress"])

    def test_delete_by_id_as_admin(self):
        self.delete_by_id_as("admin")

    def test_delete_by_id_as_seller(self):
        with self.assertRaises(UnauthorizedError):
            self.delete_by_id_as("seller")

    def test_delete_by_id_as_user(self):
        with self.assertRaises(UnauthorizedError):
            self.delete_by_id_as("user")

    def test_delete_by_id_as_anon(self):
        with self.assertRaises(UnauthorizedError):
            self.delete_by_id_as()

    def test_get_all_items_as_anon(self):
        with self.assertRaises(UnauthorizedError):
            super().test_get_all_items_as_anon()

    def test_get_by_id_as_anon(self):
        with self.assertRaises(UnauthorizedError):
            super().test_get_by_id_as_anon()
