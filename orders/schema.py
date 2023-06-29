import graphene
from graphene_django import DjangoObjectType

from users.schema import UserType
from .models import Order
from .repository import OrdersRepository


class OrderType(DjangoObjectType):
    class Meta:
        model = Order


class Query(graphene.ObjectType):
    orders = graphene.List(OrderType, searched_id=graphene.Int())

    # @permission(roles=[Admin, User])
    def resolve_orders(self, info, searched_id=None, **kwargs):
        """
        TODO add docstring

        :param searched_id:
        :param info:
        :param kwargs:
        :return:
        """
        if searched_id:
            return OrdersRepository.get_by_id(info=info,
                                              searched_id=searched_id)
        return OrdersRepository.get_all_items(info)


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
        goods_ids = graphene.List(graphene.ID, required=True)

   # @permission(roles=[Admin, User])
    def mutate(self, info,
               time_of_order,
               delivery_address,
               goods_ids):
        """
        TODO finish docs

        :param info:
        :param time_of_order:
        :param delivery_address:
        :param goods_ids:
        :return:
        """
        order = OrdersRepository.create_item(info=info,
                                             time_of_order=time_of_order,
                                             delivery_address=delivery_address,
                                             goods_ids=goods_ids
                                             )

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
    user = graphene.Field(UserType)
    delivery_status = graphene.String()
    payment_status = graphene.String()

    class Arguments:
        order_id = graphene.Int()
        delivery_address = graphene.String()

  #  @permission(roles=[Admin])
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
            user=order.user
        )


class ChangeDeliveryStatus(graphene.Mutation):
    id = graphene.Int()
    delivery_status = graphene.String()

    class Arguments:
        id = graphene.Int()
        delivery_status = graphene.String()

    def mutate(self, info, id_arg, delivery_status):

        order = OrdersRepository.change_delivery_status(
                                                info=info,
                                                id_arg=id_arg,
                                                delivery_status=delivery_status)

        return ChangeDeliveryStatus(id=order.id,
                                    delivery_status=order.delivery_status)


class ChangePaymentStatus(graphene.Mutation):
    id = graphene.Int()
    payment_status = graphene.String()

    class Arguments:
        id = graphene.Int()
        payment_status = graphene.String()

    def mutate(self, info, id_arg, payment_status):
        """
        TODO add docs

        :param info:
        :param id_arg:
        :param payment_status:
        :return:
        """
        order = OrdersRepository.change_payment_status(
                                                info=info,
                                                id_arg=id_arg,
                                                payment_status=payment_status)

        return ChangeDeliveryStatus(id=order.id,
                                    payment_status=order.payment_status)


class DeleteOrder(graphene.Mutation):
    id = graphene.Int(required=True)

    class Arguments:
        order_id = graphene.Int(required=True)

  #  @permission(roles=[Admin])
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
    change_delivery_status = ChangeDeliveryStatus.Field()
    change_payment_status = ChangePaymentStatus.Field() # intern
    update_order = UpdateOrder.Field()
    delete_order = DeleteOrder.Field()
