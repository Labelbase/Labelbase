from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def breadcrumbs_article(article):
    category = article.category
    breadcrumbs = [{'label': 'Knowledge Base', 'url': reverse('kb-index') },
                   {'label': category.name, 'url': reverse('category_detail', args=[category.slug])},
                   {'label': article.title, 'url': reverse('article_detail', args=[ article.slug])}]
    return breadcrumbs

@register.simple_tag
def breadcrumbs_category(category):
    breadcrumbs = [{'label': 'Knowledge Base', 'url': reverse('kb-index') },
                   {'label': category.name, 'url': reverse('category_detail', args=[category.slug])}]
    return breadcrumbs
