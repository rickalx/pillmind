from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

from ..models.prompt import Prompt, HistorialModificacion, RolIA
from ..forms.prompt_forms import PromptForm

class PromptListView(LoginRequiredMixin, ListView):
    """
    Vista para listar todos los prompts
    """
    model = Prompt
    template_name = 'prompts/lista_prompts.html'
    context_object_name = 'prompts'
    
    def get_queryset(self):
        """
        Usar el manager default (ya filtra por deleted_on__isnull=True)
        Solo necesitamos ordenar como queremos
        """
        return super().get_queryset().order_by('-es_predeterminado', '-fecha_ultima_modificacion')

class PromptCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear un nuevo prompt
    """
    model = Prompt
    form_class = PromptForm
    template_name = 'prompts/crear_prompt.html'
    success_url = reverse_lazy('prompt_list')
    
    def form_valid(self, form):
        """
        Asignar el usuario actual como autor del prompt
        """
        form.instance.autor = self.request.user
        return super().form_valid(form)

class PromptUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista para editar un prompt existente
    """
    model = Prompt
    form_class = PromptForm
    template_name = 'prompts/editar_prompt.html'
    success_url = reverse_lazy('prompt_list')
    
    def get_context_data(self, **kwargs):
        """
        Añadir historial de modificaciones al contexto
        """
        context = super().get_context_data(**kwargs)
        context['historial_modificaciones'] = HistorialModificacion.objects.filter(
            prompt=self.object
        ).order_by('-fecha_modificacion')
        return context

class PromptDetailView(LoginRequiredMixin, DetailView):
    """
    Vista para ver los detalles de un prompt
    """
    model = Prompt
    template_name = 'prompts/detalle_prompt.html'
    context_object_name = 'prompt'
    
    def get_context_data(self, **kwargs):
        """
        Añadir historial de modificaciones y análisis relacionados al contexto
        """
        context = super().get_context_data(**kwargs)
        
        # Historial de modificaciones
        context['historial_modificaciones'] = HistorialModificacion.objects.filter(
            prompt=self.object
        ).order_by('-fecha_modificacion')
        
        # Análisis relacionados
        context['analisis_relacionados'] = self.object.analisis_propuestas.all().order_by('-fecha_analisis')
        
        return context

class PromptSetDefaultView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            prompt = Prompt.objects.get(pk=pk)
            prompt.es_predeterminado = True
            prompt.save()
            messages.success(request, f'El prompt "{prompt.objetivo}" ha sido establecido como predeterminado para el chatbot.')
        except Prompt.DoesNotExist:
            messages.error(request, 'El prompt no existe.')
        
        return HttpResponseRedirect(reverse('prompt_list'))
