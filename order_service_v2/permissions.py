import abc
from typing import Type

from django.contrib.auth.models import AnonymousUser

from app.errors import UnauthorizedError
from users.models import ExtendedUser

"""This is an implementation of permissions and roles"""


class IUser(abc.ABCMeta):
    """Interface for roles"""

    @staticmethod
    @abc.abstractmethod
    def is_equal(role):
        pass


class Admin(IUser):
    @staticmethod
    def is_equal(role: ExtendedUser):
        if isinstance(role, AnonymousUser):
            return False
        else:
            return role.is_admin()


class User(IUser):
    @staticmethod
    def is_equal(role: ExtendedUser):
        if isinstance(role, AnonymousUser):
            return False
        else:
            return role.is_user()


class Seller(IUser):
    @staticmethod
    def is_equal(role: ExtendedUser):
        if isinstance(role, AnonymousUser):
            return False
        else:
            return role.is_seller()


class All(IUser):
    @staticmethod
    def is_equal(role):
        return True


class Anon(IUser):
    @staticmethod
    def is_equal(role):
        if isinstance(role, AnonymousUser):
            return True
        else:
            return False


def permission(roles: list[Type[IUser]] = None):
    """We use this decorator for queries and mutations


    :param roles: allowed roles. Passed at mutation/query implementation.
    :return: result of executed mutation"""
    def inner_permission(func):
        def validate_permission_scope(*arg, **kwargs):
            user = arg[1].context.user
            for allowed_role in roles:
                if allowed_role.is_equal(user):
                    return func(*arg, **kwargs)
            raise UnauthorizedError(
                "Not enough permissions to call this endpoint")
        return validate_permission_scope
    return inner_permission
