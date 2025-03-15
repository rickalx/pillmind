from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PerfilProfesional, Especialidad, NivelAcceso, Rol
from .forms import CustomUserCreationForm, CustomUserChangeForm

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

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'birth_date')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number', 'birth_date')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        print("Fieldsets:", self.fieldsets)
        return super().get_form(request, obj, **kwargs)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Especialidad)
admin.site.register(NivelAcceso)
admin.site.register(Rol)
admin.site.register(PerfilProfesional)