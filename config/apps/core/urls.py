from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path('', views.home, name="home"),
    path(
        "iniciar-sesion/",
        views.iniciar_sesion_view,
        name="iniciar_sesion"
    ),
    path(
        "cerrar-sesion/",
        views.cerrar_sesion_view,
        name="cerrar_sesion"
    ),
]