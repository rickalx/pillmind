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
    list_display = ['username', 'email', 'is_staff', 'is_verified']
    inlines = (PerfilProfesionalInline,)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'birth_date', 'gender')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
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
            'fields': ('is_staff', 'is_superuser', 'is_verified'),
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