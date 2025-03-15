from django.urls import path
from .views.analisis_propuesta_views import (
    AnalisisPropuestaCreateView,
    AnalisisPropuestaUpdateView,
    AnalisisPropuestaListView
)

urlpatterns = [
    # URLs para análisis de propuestas
    path('propuestas/', AnalisisPropuestaListView.as_view(), name='analisis_propuesta_list'),
    path('propuestas/nuevo/', AnalisisPropuestaCreateView.as_view(), name='analisis_propuesta_create'),
    path('propuestas/editar/<int:pk>/', AnalisisPropuestaUpdateView.as_view(), name='analisis_propuesta_update'),
]
