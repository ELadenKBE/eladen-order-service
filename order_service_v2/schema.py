import graphene
import graphql_jwt

import orders.schema


class Query(orders.schema.Query):
    pass


class Mutation(orders.schema.Mutation,
               graphene.ObjectType,):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
