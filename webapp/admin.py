from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PerfilProfesional, Especialidad, NivelAcceso, Rol
from .forms.custom_user_forms import CustomUserCreationForm, CustomUserChangeForm
from .models.analisis_propuesta import AnalisisPropuesta

class PerfilProfesionalInline(admin.StackedInline):
    model = PerfilProfesional
    can_delete = False
    verbose_name_plural = 'Perfil Profesional'

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'is_staff']
    inlines = (PerfilProfesionalInline,)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'birth_date', 'gender')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'phone_number', 'birth_date', 'gender'),
        }),
        ('Permisos', {
            'fields': ('is_staff', 'is_superuser'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        print("Fieldsets:", self.fieldsets)
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        # Imprime los errores del formulario en la consola
        if form.errors:
            print("Errores del formulario:", form.errors)
        super().save_model(request, obj, form, change)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Especialidad)
admin.site.register(NivelAcceso)
admin.site.register(Rol)
admin.site.register(PerfilProfesional)

@admin.register(AnalisisPropuesta)
class AnalisisPropuestaAdmin(admin.ModelAdmin):
    list_display = (
        'usuario', 
        'fecha_analisis', 
        'estado', 
        'get_resumen'
    )
    list_filter = ('estado', 'fecha_analisis')
    search_fields = ('contenido', 'usuario__username')
    readonly_fields = ('fecha_analisis', 'fecha_ultima_modificacion')

    def get_resumen(self, obj):
        return obj.get_resumen()
    get_resumen.short_description = 'Resumen'