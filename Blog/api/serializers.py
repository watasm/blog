from rest_framework import serializers
from ..models import Category, Article, Comment
from django.contrib.auth.models import User
from taggit.models import Tag
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from django.utils.text import slugify
from accounts.api.serializers import SimpleUserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'name']
        read_only_fields = ['id', 'slug']

    def create(self, validated_data):
        name = validated_data.get('name')
        catgory = Category.objects.create(slug=slugify(name), name=name)

        return catgory

    def update(self, instance, validated_data):
        slug = slugify(validated_data.get('name'))
        validated_data['slug'] = slug
        return super().update(instance, validated_data)

class CommentSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    article = serializers.PrimaryKeyRelatedField(queryset=Article.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'article', 'comment_likes', 'post_date']
        read_only_fields = ['id', 'user', 'comment_likes', 'post_date']
        depth = 1

    # def get_fields(self, *args, **kwargs):
    #     fields = super().get_fields(*args, **kwargs)
    #     request = self.context.get('request', None)
    #     if request and request.method in ("PUT", "PATCH"):
    #         fields['article'].read_only = True
    #     return fields

    def validate_article(self, value):
        if self.instance and value != self.instance.article:
            raise serializers.ValidationError('Cannot change article id.')
        return value

class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    category = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, write_only=True)
    tags = TagListSerializerField()
    # TODO: dont return text when action=list

    class Meta:
        model = Article
        fields = ['id', 'user', 'category',  'title', 'description', 'like', 'post_date', 'comments', 'category_ids', 'tags']
        read_only_fields = ['id', 'user', 'like', 'post_date']
        depth = 3

    def create(self, validated_data):
        category_ids = validated_data.pop('category_ids')
        article = Article.objects.create(**validated_data)

        for category in category_ids:
            article.category.add(category)

        return article

    def update(self, instance, validated_data):
        if 'category_ids' in validated_data:
            category_ids = validated_data.pop('category_ids')
            instance.category.clear()
            for category in category_ids:
                instance.category.add(category)

        return super().update(instance, validated_data)
