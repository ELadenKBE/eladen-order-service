import abc

from django.db.models import QuerySet
from django.db import models
from django.db.models import Q
from graphql import GraphQLResolveInfo


class IRepository(metaclass=abc.ABCMeta):
    @staticmethod
    @abc.abstractmethod
    def get_by_id(searched_id: str,
                  info: GraphQLResolveInfo = None) -> [QuerySet]:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_items_by_filter(search_filter: Q,
                            info: GraphQLResolveInfo = None) -> [QuerySet]:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_all_items(info: GraphQLResolveInfo = None) -> [QuerySet]:
        pass

    @staticmethod
    @abc.abstractmethod
    def create_item(info: GraphQLResolveInfo = None, **kwargs) -> [QuerySet]:
        pass

    @staticmethod
    @abc.abstractmethod
    def update_item(info: GraphQLResolveInfo = None, **kwargs) -> [QuerySet]:
        pass

    @staticmethod
    @abc.abstractmethod
    def delete_item(info: GraphQLResolveInfo, searched_id: str):
        pass


class RepositoryBase:

    model: models = None

    def get_items_by_filter_base(self, search_filter: Q) -> [QuerySet]:
        return self.model.objects.filter(search_filter)

    def get_by_id_base(self, searched_id: str) -> [QuerySet]:
        data_to_return = self.model.objects.get(id=searched_id)
        return [data_to_return]

    def get_all_items_base(self) -> [QuerySet]:
        return self.model.objects.all()

    def create_item_with_no_relations_base(self, **kwargs) -> [QuerySet]:
        item = self.model(**kwargs)
        item.save()
        return item

    def update_item_base(self, item_id: str, **kwargs) -> [QuerySet]:
        item = self.model.objects.filter(id=item_id).first()
        item.__dict__.update(**kwargs)
        item.save()
        return item

    def delete_item_base(self, item_id: str):
        item = self.model.objects.filter(id=item_id).first()
        item.delete()
