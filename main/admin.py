# main/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User  # Импортируем стандартного User
from .models import UserProfile, Site, Operation


# Инлайн для профиля в админке User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'


# Расширяем админку User
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'get_full_name', 'email', 'is_staff')

    def get_full_name(self, obj):
        if hasattr(obj, 'profile') and obj.profile.full_name:
            return obj.profile.full_name
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()

    get_full_name.short_description = 'ФИО'


# Админка для Site
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


# Админка для Operation
class OperationAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'operation_type', 'item_name', 'site', 'created_by', 'quantity', 'unit')
    list_filter = ('operation_type', 'site', 'created_at', 'created_by')
    search_fields = ('item_name', 'serial', 'comment')
    readonly_fields = ('created_at',)


# Регистрируем модели
admin.site.unregister(User)  # Отменяем стандартную регистрацию
admin.site.register(User, CustomUserAdmin)  # Регистрируем с нашей кастомной админкой
admin.site.register(Site, SiteAdmin)
admin.site.register(Operation, OperationAdmin)