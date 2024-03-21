from django.urls import path
from .views import ExportJSONView, ImportJSONView
from .views import CategoryDetailView, ArticleDetailView, IndexView
from .decorators import staff_required

urlpatterns = [
    path('', IndexView.as_view(), name='kb-index'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('article/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    #TODO: staff only,
    path('export', staff_required(ExportJSONView.as_view()), name='export_json'),
    path('import', staff_required(ImportJSONView.as_view()), name='import_json'),
]
