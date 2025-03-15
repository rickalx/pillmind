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
    template_name = 'propuestas/analisis_propuesta.html'
    success_url = reverse_lazy('analisis_propuesta_list')
    
    def get_queryset(self):
        # Permitir editar análisis del usuario actual o donde el nombre de usuario coincide
        return AnalisisPropuesta.objects.filter(
            Q(usuario=self.request.user) | 
            Q(nombre_usuario=self.request.user.username)
        )

class AnalisisPropuestaListView(LoginRequiredMixin, ListView):
    model = AnalisisPropuesta
    template_name = 'propuestas/lista_analisis.html'
    context_object_name = 'analisis_propuestas'

    def get_queryset(self):
        # Mostrar análisis del usuario actual o análisis donde el nombre de usuario coincide
        # (para casos donde el usuario fue eliminado pero queremos ver sus análisis)
        return AnalisisPropuesta.objects.filter(
            Q(usuario=self.request.user) | 
            Q(nombre_usuario=self.request.user.username)
        )
