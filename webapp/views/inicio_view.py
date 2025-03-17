from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class InicioView(TemplateView):
    template_name = 'inicio.html'