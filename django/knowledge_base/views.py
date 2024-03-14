from django.http import JsonResponse
from django.shortcuts import render
import json
from django.views.generic import View, ListView, DetailView
from .models import Category, Article, ExportSnapshot
from .forms import JSONUploadForm
from django.utils.text import slugify

class ExportJSONView(View):
    def get(self, request):
        categories = Category.objects.all().exclude(exclude_from_export=True)
        data = {}
        for category in categories:
            articles = list(category.article_set.all().exclude(exclude_from_export=True).values())
            data[category.name] = articles
        export_snapshot = ExportSnapshot.objects.create(
            exported_data=data
        )
        return JsonResponse(data)


class ImportJSONView(View):
    def get(self, request):
        form = JSONUploadForm()
        return render(request, 'knowledge_base/import_json.html', {'form': form})

    def post(self, request):
        form = JSONUploadForm(request.POST, request.FILES)
        if form.is_valid():
            json_file = request.FILES['json_file']
            try:
                content = json_file.read().decode('utf-8')
                data = json.loads(content)

                for category_name, articles in data.items():
                    try:
                        category = Category.objects.get(slug=slugify(category_name))
                    except Category.DoesNotExist:
                        category = Category.objects.create(name=category_name,
                                                            slug=slugify(category_name))

                    for article_data in articles:
                        try:
                            article = Article.objects.get(slug=article_data['slug'])
                            article.title = article_data['title']
                            article.content = article_data['content']
                            article.category = category
                            article.save()
                        except Article.DoesNotExist:
                            Article.objects.create(title=article_data['title'],
                                                    content=article_data['content'],
                                                    category=category,
                                                    slug=article_data['slug'])
                return JsonResponse({'message': 'Import successful'})
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid form data'}, status=400)


class IndexView(ListView):
    model = Category
    template_name = 'knowledge_base/index.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'knowledge_base/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'knowledge_base/article_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'
