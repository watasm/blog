from rest_framework import serializers

from quiz.models import Quiz, Question, QuestionChoices, QuestionAnswer
from blog.models import Category

from blog.api.serializers import CategorySerializer
from accounts.api.serializers import SimpleUserSerializer

from rest_framework.permissions import SAFE_METHODS

class QuestionChoicesSerializer(serializers.ModelSerializer):
    is_right_choice = serializers.BooleanField(write_only=True)

    class Meta:
        model = QuestionChoices
        fields = ['choice', 'is_right_choice']

class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    order = serializers.IntegerField(min_value=0, read_only=True)
    choices = QuestionChoicesSerializer(many=True)
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), write_only=True)

    class Meta:
        model = Question
        fields = ['id', 'url', 'order', 'quiz', 'question', 'choices']

    def validate_quiz(self, value):
        if value in self.context['request'].user.created_quizzes.all():
            raise serializers.ValidationError('Error. Cannot change quiz.')
        return value

    def create(self, validated_data):
        choices = validated_data.pop('choices')
        question = Question.objects.create(**validated_data)

        for choice in choices:
            QuestionChoices.objects.create(choice=choice['choice'], is_right_choice=choice['is_right_choice'], question=question)

        return question

class QuizSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    user = SimpleUserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = '__all__'

    def create(self, validated_data):
        validated_data['category'] = validated_data.pop('category_id')
        return super().create(validated_data)
