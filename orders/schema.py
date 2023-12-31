import graphene
from decouple import config
from django.forms.models import model_to_dict

from order_service_v2.authorization import grant_authorization
from order_service_v2.checkout_producer import CheckoutProducer
from order_service_v2.product_service import ProductService, GoodType
from .models import Order
from .repository import OrdersRepository

product_service = ProductService()
checkout_producer = CheckoutProducer()


class OrderType(graphene.ObjectType):
    id = graphene.Int()
    time_of_order = graphene.String()
    items_price = graphene.Decimal()
    delivery_price = graphene.Decimal()
    user_id = graphene.Int()
    delivery_status = graphene.String()
    payment_status = graphene.String()
    goods = graphene.List(GoodType)
    delivery_address = graphene.String()

    def __init__(self,
                 id,
                 goods=None,
                 user_id=None,
                 delivery_status=None,
                 time_of_order=None,
                 delivery_address=None,
                 items_price=None,
                 delivery_price=None,
                 payment_status=None,
                 ):
        self.id = id
        self.user_id = user_id
        self.goods = goods
        self.time_of_order = time_of_order
        self.items_price = items_price
        self.delivery_price = delivery_price
        self.delivery_status = delivery_status
        self.payment_status = payment_status
        self.delivery_address = delivery_address


def get_goods_of_order(dict_response, info):
    goods_ids = dict_response['goods_ids']
    del dict_response['goods_ids']
    request_query = info.context.body.decode('utf-8')
    has_goods = 'goods' in request_query
    if has_goods:
        goods = product_service.get_goods_by_ids(info, goods_ids)
        return goods
    else:
        return []


def get_response(info):
    pass


class Query(graphene.ObjectType):
    orders = graphene.List(OrderType, searched_id=graphene.Int())

    @grant_authorization
    def resolve_orders(self, info, searched_id=None, **kwargs):
        """
        TODO add docstring

        :param searched_id:
        :param info:
        :param kwargs:
        :return:
        """
        if searched_id:
            order: Order = OrdersRepository.get_by_id(
                                                info=info,
                                                searched_id=searched_id)
            order_dict = model_to_dict(order)
            goods = get_goods_of_order(order_dict, info)
            return [OrderType(goods=goods, **order_dict)]
        orders = OrdersRepository.get_all_items(info)
        list_with_orders = []
        for order in orders:
            order_dict = model_to_dict(order)
            goods = get_goods_of_order(order_dict, info)
            list_with_orders.append(OrderType(goods=goods, **order_dict))
        return list_with_orders


class CreateOrder(graphene.Mutation):
    id = graphene.Int()
    time_of_order = graphene.String()
    delivery_address = graphene.String()
    items_price = graphene.Float()
    delivery_price = graphene.Float()
    user_id = graphene.Int()
    delivery_status = graphene.String()
    payment_status = graphene.String()
    goods_ids = graphene.List(graphene.Int)

    class Arguments:
        time_of_order = graphene.String()
        delivery_address = graphene.String()

    @grant_authorization
    def mutate(self, info, time_of_order, delivery_address):
        """
        TODO finish docs
        TODO create a new abstraction layer for handling services

        :param info:
        :param time_of_order:
        :param delivery_address:
        :return:
        """
        ids_in_cart = product_service.get_cart(info)
        order: Order = OrdersRepository.create_item_with_foreign_ids(
            goods_ids_in_cart=ids_in_cart,
            info=info,
            time_of_order=time_of_order,
            delivery_address=delivery_address)
        # local_mode = config('LOCAL_MODE', default=False, cast=bool)
        # # if local_mode:
        # #     print("Local mode is on! connection to rabbitmq is off")
        # else:
        checkout_producer.publish_order(order)

        return CreateOrder(
            id=order.id,
            delivery_address=order.delivery_address,
            items_price=order.items_price,
            delivery_price=order.delivery_price,
            time_of_order=order.time_of_order,
            user_id=order.user_id,
            delivery_status=order.delivery_status,
            payment_status=order.payment_status,
            goods_ids=order.goods_ids
        )


class UpdateOrder(graphene.Mutation):
    id = graphene.Int()
    time_of_order = graphene.String()
    delivery_address = graphene.String()
    items_price = graphene.Float()
    delivery_price = graphene.Float()
    user_id = graphene.Int()
    delivery_status = graphene.String()
    payment_status = graphene.String()

    class Arguments:
        order_id = graphene.Int()
        delivery_address = graphene.String()

    @grant_authorization
    def mutate(self, info,
               order_id,
               delivery_address=None):
        """
        TODO add docs

        :param info:
        :param order_id:
        :param delivery_address:
        :return:
        """
        order = OrdersRepository.update_item(info=info,
                                             order_id=order_id,
                                             delivery_address=delivery_address)

        return UpdateOrder(
            id=order.id,
            delivery_address=order.delivery_address,
            items_price=order.items_price,
            delivery_price=order.delivery_price,
            time_of_order=order.time_of_order,
            user_id=order.user_id
        )


class ChangeDeliveryStatus(graphene.Mutation):
    id = graphene.Int()
    delivery_status = graphene.String()

    class Arguments:
        id = graphene.Int()
        delivery_status = graphene.String()

    def mutate(self, info, id, delivery_status):

        order = OrdersRepository.change_delivery_status(
                                                info=info,
                                                id_arg=id,
                                                delivery_status=delivery_status)

        return ChangeDeliveryStatus(id=order.id,
                                    delivery_status=order.delivery_status)


class ChangePaymentStatus(graphene.Mutation):
    id = graphene.Int()
    payment_status = graphene.String()

    class Arguments:
        id = graphene.Int()
        payment_status = graphene.String()

    def mutate(self, info, id, payment_status):
        """
        TODO add docs

        :param info:
        :param id_arg:
        :param payment_status:
        :return:
        """
        order = OrdersRepository.change_payment_status(
                                                info=info,
                                                id_arg=id,
                                                payment_status=payment_status)

        return ChangePaymentStatus(id=order.id,
                                   payment_status=order.payment_status)


class DeleteOrder(graphene.Mutation):
    id = graphene.Int(required=True)

    class Arguments:
        order_id = graphene.Int(required=True)

    @grant_authorization
    def mutate(self, info, order_id):
        """
        TODO add docs

        :param info:
        :param order_id:
        :return:
        """
        OrdersRepository.delete_item(info=info, searched_id=order_id)
        return DeleteOrder(
            id=order_id
        )


class Mutation(graphene.ObjectType):
    create_order = CreateOrder.Field()
    change_delivery_status = ChangeDeliveryStatus.Field() # intern
    change_payment_status = ChangePaymentStatus.Field() # intern
    update_order = UpdateOrder.Field()
    delete_order = DeleteOrder.Field()
