import graphene
from graphene_django import DjangoObjectType

from users.models import ExtendedUser


class UserType(DjangoObjectType):
    class Meta:
        model = ExtendedUser


class CreateUser(graphene.Mutation):
    id = graphene.Int()
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    role = graphene.Int(required=True)
    address = graphene.String()
    firstname = graphene.String()
    lastname = graphene.String()
    image = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)
        role = graphene.Int(required=True)
        address = graphene.String()
        firstname = graphene.String()
        lastname = graphene.String()
        image = graphene.String()

    def mutate(self,
               info,
               username,
               password,
               email,
               role,
               image=None,
               address=None,
               firstname=None,
               lastname=None):
        """
        TODO add docs

        :param info:
        :param username:
        :param password:
        :param email:
        :param role:
        :param image:
        :param address:
        :param firstname:
        :param lastname:
        :return:
        """

        user = ExtendedUser(
            username=username,
            email=email,
            role=role,
            address=address,
            lastname=lastname,
            firstname=firstname,
            image=image
        )
        user.set_password(password)
        user.save()
        return CreateUser(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            address=user.address,
            lastname=user.lastname,
            firstname=user.firstname,
            image=user.image
        )


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
