from django.urls import path

from apps.asistente.views import recomendar_plantilla_view


app_name = "asistente"

urlpatterns = [
    path(
        "recomendar/",
        recomendar_plantilla_view,
        name="recomendar_plantilla"
    ),
]