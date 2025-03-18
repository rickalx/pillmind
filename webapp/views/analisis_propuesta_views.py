from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from ..models.analisis_propuesta import AnalisisPropuesta
from ..forms import AnalisisPropuestaForm

class AnalisisPropuestaCreateView(LoginRequiredMixin, CreateView):
    model = AnalisisPropuesta
    form_class = AnalisisPropuestaForm
    template_name = 'propuestas/crear_analisis.html'
    success_url = reverse_lazy('analisis_propuesta_list')

    def form_valid(self, form):
        # Asignar el usuario actual
        form.instance.usuario = self.request.user
        
        # Guardar información del usuario para preservarla
        form.instance.nombre_usuario = self.request.user.username
        form.instance.email_usuario = self.request.user.email
        
        return super().form_valid(form)

class AnalisisPropuestaUpdateView(LoginRequiredMixin, UpdateView):
    model = AnalisisPropuesta
    form_class = AnalisisPropuestaForm
    template_name = 'propuestas/editar_analisis_propuesta.html'
    success_url = reverse_lazy('analisis_propuesta_list')
    
    # No get_queryset method - allows editing any proposal for logged-in users

class AnalisisPropuestaListView(ListView):  # Not LoginRequiredMixin - allows all users to view list
    model = AnalisisPropuesta
    template_name = 'propuestas/lista_analisis.html'
    context_object_name = 'analisis_propuestas'

    def get_queryset(self):
        # Return all proposals without filtering by user
        return AnalisisPropuesta.objects.all()
