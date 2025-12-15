# ProyectoV/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'base.html')

def nosotros(request):
    return render(request, 'nosotros.html')
def inicio(request):
    return render(request, 'inicio.html')