from django.urls import path
from .views.analisis_propuesta_views import (
    AnalisisPropuestaCreateView,
    AnalisisPropuestaUpdateView,
    AnalisisPropuestaListView
)
from .views.analisis_propuesta_detail_view import AnalisisPropuestaDetailView
from .views.prompt_views import (
    PromptListView,
    PromptCreateView,
    PromptUpdateView,
    PromptDetailView
)
from .views.rol_ia_views import RolIACreateView
from .views.inicio_view import InicioView

urlpatterns = [
    # URL para la página de inicio
    path('', InicioView.as_view(), name='inicio'),
    
    # URLs para análisis de propuestas
    path('propuestas/', AnalisisPropuestaListView.as_view(), name='analisis_propuesta_list'),
    path('propuestas/nuevo/', AnalisisPropuestaCreateView.as_view(), name='analisis_propuesta_create'),
    path('propuestas/editar/<int:pk>/', AnalisisPropuestaUpdateView.as_view(), name='analisis_propuesta_update'),
    path('propuestas/detalle/<int:pk>/', AnalisisPropuestaDetailView.as_view(), name='analisis_propuesta_detail'),
    
    # URLs para prompts
    path('prompts/', PromptListView.as_view(), name='prompt_list'),
    path('prompts/nuevo/', PromptCreateView.as_view(), name='prompt_create'),
    path('prompts/editar/<pk>/', PromptUpdateView.as_view(), name='prompt_update'),
    path('prompts/detalle/<uuid:pk>/', PromptDetailView.as_view(), name='prompt_detail'),
    
    # URLs para roles de IA
    path('roles-ia/nuevo/', RolIACreateView.as_view(), name='rol_ia_add'),
]
