from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Site, Operation, OperationType
from django.contrib.auth.models import User
from django.utils import timezone


@login_required(login_url='/login/')
def home(request):
    # Получаем данные для формы (ВЫНОСИМ ЭТО В НАЧАЛО!)
    sites = Site.objects.all()

    # Обработка формы создания операции
    if request.method == 'POST':
        try:
            operation = Operation(
                operation_type=request.POST['operation_type'],
                created_by=request.user,
                item_name=request.POST['item_name'],
                serial=request.POST.get('serial', ''),
                quantity=float(request.POST['quantity']),
                unit=request.POST['unit'],
                comment=request.POST.get('comment', '')
            )

            # НОВАЯ ЛОГИКА: заполняем from_site и to_site в зависимости от типа операции
            op_type = request.POST['operation_type']

            if op_type == OperationType.MOVE:
                # Перемещение: оба склада обязательны
                operation.from_site_id = request.POST['from_site']
                operation.to_site_id = request.POST['to_site']
                if not operation.from_site_id or not operation.to_site_id:
                    messages.error(request, 'Для перемещения укажите "Откуда" и "Куда"')
                    return redirect('/')

            elif op_type == OperationType.INCOMING:
                # Приход: только "Куда" обязательно
                operation.to_site_id = request.POST['to_site']
                if not operation.to_site_id:
                    messages.error(request, 'Для прихода укажите "Куда"')
                    return redirect('/')

            elif op_type == OperationType.WRITEOFF:
                # Списание: только "Откуда" обязательно
                operation.from_site_id = request.POST['from_site']
                if not operation.from_site_id:
                    messages.error(request, 'Для списания укажите "Откуда"')
                    return redirect('/')

            operation.save()
            messages.success(request, f'Операция "{operation.get_operation_type_display()}" создана!')
            return redirect('/')

        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return redirect('/')

    # Операции за сегодня
    today = timezone.now().date()
    today_operations = Operation.objects.filter(
        created_at__date=today
    ).select_related('from_site', 'to_site', 'created_by').order_by('-created_at')[:50]

    # Последние 10 операций
    last_operations = Operation.objects.all().select_related('from_site', 'to_site', 'created_by').order_by(
        '-created_at')[:10]

    context = {
        'sites': sites,  # Теперь переменная определена
        'today_operations': today_operations,
        'last_operations': last_operations,
        'operation_types': OperationType.choices,
    }

    return render(request, 'main/home.html', context)