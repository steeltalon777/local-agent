# main/models.py
from django.db import models
from django.contrib.auth.models import User  # Используем стандартного User


# Профиль пользователя с ФИО
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField('ФИО', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return self.full_name or self.user.username

    def save(self, *args, **kwargs):
        # Автоматически заполняем full_name, если не указано
        if not self.full_name and (self.user.first_name or self.user.last_name):
            self.full_name = f"{self.user.first_name or ''} {self.user.last_name or ''}".strip()
        super().save(*args, **kwargs)


# Объект (склад/участок) - оставляем как есть
class Site(models.Model):
    name = models.CharField('Наименование объекта', max_length=255, unique=True)
    code = models.CharField('Короткий код', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'

    def __str__(self):
        return self.name


# Типы операций - оставляем как есть
class OperationType(models.TextChoices):
    INCOMING = 'incoming', 'Приход'
    MOVE = 'move', 'Перемещение'
    WRITEOFF = 'writeoff', 'Списание'


# Операция движения - меняем created_by на стандартного User
class Operation(models.Model):
    created_at = models.DateTimeField('Дата и время создания', auto_now_add=True)
    operation_type = models.CharField(
        'Тип операции',
        max_length=20,
        choices=OperationType.choices
    )
    site = models.ForeignKey(Site, on_delete=models.PROTECT, verbose_name='Объект')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Создал')  # Стандартный User
    item_name = models.CharField('Наименование', max_length=255)
    serial = models.CharField('Серийный номер', max_length=255, blank=True, null=True)
    quantity = models.FloatField('Количество', default=1)
    unit = models.CharField('Единица измерения', max_length=50, default='шт')
    from_location = models.CharField('Откуда', max_length=255, blank=True, null=True)
    to_location = models.CharField('Куда', max_length=255, blank=True, null=True)
    comment = models.TextField('Комментарий', blank=True, null=True)

    class Meta:
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_operation_type_display()} - {self.item_name}'