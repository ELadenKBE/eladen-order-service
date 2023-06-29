import ast
import json
import re

import graphene
import requests
from decouple import config
from graphene_django import DjangoObjectType
from graphql import GraphQLResolveInfo

from order_service_v2.errors import ResponseError, ValidationError
from categories.models import Category
from goods.models import Good
from goods_lists.models import GoodsList
from users.models import ExtendedUser
from users.schema import UserType


class GoodType(DjangoObjectType):

    class Meta:
        model = Good


class CategoryType(DjangoObjectType):

    class Meta:
        model = Category


class GoodsListType(DjangoObjectType):

    class Meta:
        model = GoodsList


class GoodsListTransferType(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    user = graphene.Field(UserType)
    goods = graphene.List(GoodType)

    def __init__(self, id=None, title=None, user=None, goods=None):
        self.id = id
        self.title = title
        self.user = user
        self.goods = goods


def verify_connection(func):
    def wrapper(*args, **kwargs):
        try:
            introspection_query = {
                "query": """
                            query {
                                __schema {
                                    queryType {
                                        name
                                    }
                                }
                            }
                        """
            }
            response = requests.post(ProductService.url,
                                     json=introspection_query)
            if response.status_code == 200:
                pass
            else:
                raise ResponseError("Product Service is not answering")
        except requests.exceptions.RequestException:
            raise ResponseError("Product Service is not answering")
        return func(*args, **kwargs)

    return wrapper


def create_good_filler(**params):
    category_dict = None
    seller_dict = None
    if 'category' in params:
        category_dict = params['category']
        del params['category']
    if 'seller' in params:
        seller_dict = params['seller']
        del params['seller']
    if seller_dict is not None and category_dict is not None:
        return Good(
            **params,
            category=Category(**category_dict),
            seller=ExtendedUser(**seller_dict)
        )
    elif seller_dict is None and category_dict is not None:
        return Good(
            **params,
            category=Category(**category_dict)
        )
    elif seller_dict is not None and category_dict is  None:
        return Good(
            **params,
            seller=ExtendedUser(**seller_dict)
        )
    else:
        return Good(**params)


def create_goods_list_filler(**params) -> GoodsListTransferType:
    user_dict = None
    goods_dict = None
    if 'user' in params:
        user_dict = params['user']
        del params['user']
    if 'goods' in params:
        goods_dict = params['goods']
        del params['goods']
    if user_dict is not None and goods_dict is not None:
        goods = [Good(**param) for param in goods_dict]
        goods_list = GoodsListTransferType(**params,
                                           user=ExtendedUser(**user_dict),
                                           goods=goods)
        return goods_list
    if user_dict is not None and goods_dict is None:
        goods_list = GoodsListTransferType(**params,
                                           user=ExtendedUser(**user_dict))
        return goods_list
    else:
        type_object = GoodsListTransferType(**params)
        return type_object


class ProductService:

    url = config('PRODUCT_SERVICE_URL', default=False, cast=str)

    def _execute_query(self, query):
        response = requests.post(self.url, data={'query': query})
        self.validate_errors(response)
        return response

    def _request(self, info: GraphQLResolveInfo):
        cleaned = info.context.body.decode('utf-8') \
            .replace('\\n', ' ') \
            .replace('\\t', ' ')
        query = json.loads(cleaned)['query']
        return self._execute_query(query)

    @verify_connection
    def _get_data(self, entity_name: str, info: GraphQLResolveInfo):
        response = self._request(info=info)
        data = response.json().get('data', {})
        return data.get(entity_name, [])

    @staticmethod
    def validate_errors(response):
        if 'errors' in str(response.content):
            cleaned_json = json.loads(
                response.content.decode('utf-8').replace("/", "")
            )['errors']
            raise ValidationError(cleaned_json[0]['message'])

    @verify_connection
    def _create_item(self, entity_name: str, info: GraphQLResolveInfo):
        item = self._get_data(info=info, entity_name=entity_name)
        return item

    def get_categories(self, info: GraphQLResolveInfo = None):
        items_list = self._get_data(entity_name='categories', info=info)
        return [Category(**item) for item in items_list]

    def get_goods(self, info: GraphQLResolveInfo = None):
        items_list = self._get_data(entity_name='goods', info=info)
        return [create_good_filler(**item) for item in items_list]

    def get_good_lists(self, info: GraphQLResolveInfo = None):
        items_list = self._get_data(entity_name='goodsLists', info=info)
        return [create_goods_list_filler(**item) for item in items_list]

    def create_good(self, info: GraphQLResolveInfo):
        created_item_dict = self._create_item(info=info,
                                              entity_name="createGood")
        created_item = create_good_filler(**created_item_dict)
        return created_item

    def create_category(self, info: GraphQLResolveInfo):
        created_item_in_dict = self._create_item(info=info,
                                                 entity_name='createCategory')
        return Category(**created_item_in_dict)

    def create_goods_list(self, info: GraphQLResolveInfo):
        created_item_in_dict = self._create_item(info=info,
                                                 entity_name='createGoodsList')
        created_item = create_goods_list_filler(**created_item_in_dict)
        return created_item

    def update_category(self, info: GraphQLResolveInfo):
        created_item_in_dict = self._get_data(entity_name='updateCategory',
                                              info=info)
        return Category(**created_item_in_dict)

    def update_goods_list(self, info: GraphQLResolveInfo):
        created_item_in_dict = self._get_data(entity_name='updateGoodsList',
                                              info=info)
        created_item = create_goods_list_filler(**created_item_in_dict)
        return created_item

    def update_good(self, info: GraphQLResolveInfo):
        created_item_in_dict = self._get_data(entity_name='updateGood',
                                              info=info)
        created_item = create_good_filler(**created_item_in_dict)
        return created_item

    def delete_goods_list(self, info: GraphQLResolveInfo):
        self._get_data(info=info, entity_name='deleteGoodsList')

    def delete_good(self, info: GraphQLResolveInfo):
        self._get_data(info=info, entity_name='deleteGood')

    def delete_category(self, info: GraphQLResolveInfo):
        self._get_data(info=info, entity_name='deleteCategory')

    def change_goods_category(self, info):
        item_in_dict = self._get_data(info=info, entity_name='changeCategory')
        return create_good_filler(**item_in_dict)

    def add_good_to_cart(self, info):
        item_in_dict = self._get_data(info=info, entity_name='addGoodToCart')
        return create_good_filler(**item_in_dict)

    def clean_goods_list(self, info):
        item_in_dict = self._get_data(info=info, entity_name='cleanGoodsList')
        return create_goods_list_filler(**item_in_dict)

    def get_goods_by_ids(self, info, goods_ids):
        # str to int list
        goods_ids = ast.literal_eval(goods_ids)
        cleaned = info.context.body.decode('utf-8') \
            .replace('\\n', ' ') \
            .replace('\\t', ' ')
        query = json.loads(cleaned)['query']
        pattern = r'goods\s*{([^}]*)}'
        body_attr = re.search(pattern, query).group(1)
        query_string = '''{{
              goods(searchedId: {id}) {{
               {attr}
              }}
            }}'''
        queries = [query_string.format(id=x, attr=body_attr)
                   for x in goods_ids]
        goods_dicts = [self._execute_query(query).json().get('data', {})['goods'][0]
                  for query in queries]
        goods = [create_good_filler(**d) for d in goods_dicts]
        return goods