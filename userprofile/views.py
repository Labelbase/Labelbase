from django.shortcuts import render
from django.views.generic import  TemplateView # FormView,

class ProfileView(TemplateView):
    template_name = 'profile.html'
