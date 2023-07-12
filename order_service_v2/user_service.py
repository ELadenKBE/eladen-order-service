import requests
from decouple import config
from graphene_django import DjangoObjectType

from order_service_v2.base_service import BaseService
from users.models import ExtendedUser


class UserType(DjangoObjectType):
    class Meta:
        model = ExtendedUser


class UserService(BaseService):

    url = config('USER_SERVICE_URL', default=False, cast=str)
    service_name = 'User'

    def get_user(self, user_id):
        """

        :param info:
        :return:
        """
        self.verify_connection()
        query_template = """query{{
                  users(searchedId: {0}){{
                            id
                            username
                            email
                            role
                            address
                            firstName
                            lastName
                      }}
                }}"""

        query = query_template.format(int(user_id))
        response = requests.post(self.url, data={'query': query})
        user_in_dict = response.json().get('data', {}).get('users')[0]
        user = ExtendedUser(**user_in_dict)
        return user
