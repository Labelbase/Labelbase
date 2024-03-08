from django.urls import path
from .views import ExportJSONView, ImportJSONView
from .views import CategoryDetailView, ArticleDetailView, IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='kb-index'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('article/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    #TODO: staff only,
    path('export', ExportJSONView.as_view(), name='export_json'),
    #TODO: staff only,
    path('import', ImportJSONView.as_view(), name='import_json'),
]
