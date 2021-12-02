from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from core.models import (
    Category,
    Product
)


@registry.register_document
class CategoryDocument(Document):
    
    class Index:
        name = 'categories'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Category
        fields = [
            "id",
            "title",
        ]


@registry.register_document
class ProductDocument(Document):
    
    category = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "title": fields.KeywordField()
        }
    )
    
    class Index:
        name = 'products'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Product
        fields = [
            "id",
            "title",
            "price",
            "description",
            "image_url"
        ]
        related_models = [Category, ]

    def get_queryset(self):
        return super(ProductDocument, self).get_queryset().select_related("category")

    def get_instances_from_related(self, related_instance):
        return related_instance.category_products.all()
    