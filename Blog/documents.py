from django_elasticsearch_dsl import Document, fields, Index
from django_elasticsearch_dsl.registries import registry
from .models import Category, Article, Comment


article = Index('Article')


# @registry.register_document
# class CategoryDocument(Document):
#     class Index:
#         name = 'category'
#         # See Elasticsearch Indices API reference for available settings
#         # settings = {'number_of_shards': 1,
#         #             'number_of_replicas': 0}

#     class Django:
#         model = Category
#         fields = ['name']

#         # Ignore auto updating of Elasticsearch when a model is saved
#         # or deleted:
#         # ignore_signals = True

#         # Don't perform an index refresh after every update (overrides global setting):
#         # auto_refresh = False

#         # Paginate the django queryset used to populate the index with the specified size
#         # (by default it uses the database driver's default setting)
#         # queryset_pagination = 5000

@registry.register_document
class ArticleDocument(Document):
    category = fields.ObjectField(properties={
        'name': fields.TextField(),
    })

    class Index:
        name = 'articles'

    class Django:
        model = Article
        fields = ['id', 'title', 'text']

        related_models = [Category]

    def get_queryset(self):
        return super().get_queryset().prefetch_related('category')

    # def get_instances_from_related(self, related_instance):
    #     if isinstance(related_instance, Category):
    #         return related_instance.category.all()

        return None
