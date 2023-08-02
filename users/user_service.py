import requests
from decouple import config
from graphene_django import DjangoObjectType

from order_service_v2.base_service import BaseService
from order_service_v2.errors import ResponseError
from users.models import ExtendedUser


class UserType(DjangoObjectType):
    class Meta:
        model = ExtendedUser


class UserService(BaseService):

    def __init__(self):
        local_mode = config('LOCAL_MODE', default=False, cast=bool)
        if local_mode:
            self.url = config('USER_SERVICE_URL',
                              default="http://user-identity:8081/graphql/",
                              cast=str)
        else:
            self.url = "http://user-identity:8081/graphql/"
        self.service_name = 'User'

    def get_user(self, sub: str):
        """

        :param sub:
        :return:
        """
        self.verify_connection()
        query_template = """query{{
                  users(sub: "{0}"){{
                            id
                            username
                            email
                            role
                            address
                            firstName
                            lastName
                            sub
                      }}
                }}"""

        query = query_template.format(sub)
        response = requests.post(self.url, data={'query': query})
        user_in_dict = response.json().get('data', {}).get('users')[0]
        if user_in_dict is None:
            raise ResponseError('User not found')
        user = ExtendedUser(**user_in_dict)
        return user
