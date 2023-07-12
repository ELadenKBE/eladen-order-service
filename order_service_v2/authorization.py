from order_service_v2.errors import UnauthorizedError, ResponseError
from order_service_v2.user_service import UserService

user_service = UserService()


def grant_authorization(func):
    """This decorator extracts id of user from AUTHORIZATION header
    and requests a user service to get a user information"""
    def wrapper(*arg, **kwargs):
        info = arg[1]
        try:
            user_id = int(info.context.headers['AUTHORIZATION'])
            info.context.user = user_service.get_user(user_id=user_id)
        except KeyError as key_error:
            raise UnauthorizedError('authorization error: AUTHORIZATION header'
                                    ' is not specified')
        except ResponseError as response_error:
            raise UnauthorizedError('authorization error: ',
                                    response_error.args[0])
        except Exception as error:
            # TODO specify exceptions at testing
            raise UnauthorizedError('authorization error: ', error)
        return func(*arg, **kwargs)
    return wrapper
