from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from ..models.analisis_propuesta import AnalisisPropuesta

class AnalisisPropuestaDetailView(LoginRequiredMixin, DetailView):
    """
    Vista para ver los detalles de un análisis de propuesta
    """
    model = AnalisisPropuesta
    template_name = 'propuestas/detalle_analisis.html'
    context_object_name = 'analisis'
