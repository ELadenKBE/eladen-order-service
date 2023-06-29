import graphene
import graphql_jwt

import orders.schema
import users.schema


class Query(orders.schema.Query):
    pass


class Mutation(orders.schema.Mutation,
               users.schema.Mutation,
               graphene.ObjectType,):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
