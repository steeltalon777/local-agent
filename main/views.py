from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Site, Operation, OperationType
from django.contrib.auth.models import User
from django.utils import timezone


@login_required(login_url='/login/')
def home(request):
    # Обработка формы создания операции
    if request.method == 'POST':
        try:
            operation = Operation(
                operation_type=request.POST['operation_type'],
                site_id=request.POST['site'],
                created_by=request.user,
                item_name=request.POST['item_name'],
                serial=request.POST.get('serial', ''),
                quantity=float(request.POST['quantity']),
                unit=request.POST['unit'],
                from_location=request.POST.get('from_location', ''),
                to_location=request.POST.get('to_location', ''),
                comment=request.POST.get('comment', '')
            )

            # Базовая валидация по ТЗ
            if operation.operation_type == OperationType.MOVE:
                if not operation.from_location or not operation.to_location:
                    messages.error(request, 'Для перемещения укажите "Откуда" и "Куда"')
                    return redirect('/')
            elif operation.operation_type == OperationType.INCOMING:
                if not operation.to_location:
                    messages.error(request, 'Для прихода укажите "Куда"')
                    return redirect('/')
            elif operation.operation_type == OperationType.WRITEOFF:
                if not operation.from_location:
                    messages.error(request, 'Для списания укажите "Откуда"')
                    return redirect('/')

            operation.save()
            messages.success(request, f'Операция "{operation.get_operation_type_display()}" создана!')
            return redirect('/')

        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return redirect('/')

    # Получаем данные для формы и отображения
    sites = Site.objects.all()

    # Операции за сегодня
    today = timezone.now().date()
    today_operations = Operation.objects.filter(
        created_at__date=today
    ).select_related('site', 'created_by').order_by('-created_at')[:50]

    # Последние 10 операций (все)
    last_operations = Operation.objects.all().select_related('site', 'created_by').order_by('-created_at')[:10]

    context = {
        'sites': sites,
        'today_operations': today_operations,
        'last_operations': last_operations,
        'operation_types': OperationType.choices,
    }

    return render(request, 'main/home.html', context)