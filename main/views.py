from django.shortcuts import render
from django.http import HttpResponse

def home_page(request):
    return HttpResponse("""
        <h1>🎉 Мой первый Django проект работает!</h1>
        <p>Привет от приложения 'main'!</p>
        <p><a href="/admin/">Админка Django</a></p>
    """)


