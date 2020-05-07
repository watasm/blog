from django.contrib import admin
from blog.models import Article, Category, Comment
from django_summernote.admin import SummernoteModelAdmin

admin.site.index_template = 'memcache_status/admin_index.html'

class CommentInline(admin.StackedInline):
    model=Comment

class ArticleAdmin(SummernoteModelAdmin):
    summernote_fields = ('text',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}

admin.site.register(Article, ArticleAdmin)

admin.site.register(Comment)
