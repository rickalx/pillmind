from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from ..models.prompt import RolIA
from ..forms.rol_ia_forms import RolIAForm

class RolIACreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear un nuevo rol de IA
    """
    model = RolIA
    form_class = RolIAForm
    template_name = 'roles_ia/crear_rol_ia.html'
    
    def get_success_url(self):
        """
        Redirigir a la página de creación de prompts
        """
        # Si la solicitud viene de una ventana emergente, cerrar la ventana
        if '_popup' in self.request.GET:
            return None
        return reverse_lazy('prompt_create')
    
    def form_valid(self, form):
        """
        Mostrar mensaje de éxito al crear un rol
        """
        response = super().form_valid(form)
        
        # Si la solicitud viene de una ventana emergente, cerrar la ventana
        if '_popup' in self.request.GET:
            # Pasar el objeto creado al template
            return self.render_to_response(self.get_context_data(form=form, object=self.object))
        
        messages.success(self.request, _('Rol de IA creado exitosamente'))
        return response
