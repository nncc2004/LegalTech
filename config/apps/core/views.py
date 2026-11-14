from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.

def home(request):
    
    return render(request, 'home.html')

def iniciar_sesion_view(request):

    if request.user.is_authenticated:
        return redirect("documentos:biblioteca")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            return redirect("core:home")

        messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "../templates/iniciar_sesion.html")


def cerrar_sesion_view(request):
    logout(request)
    return redirect("core:home")