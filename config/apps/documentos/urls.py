from django.urls import path

from apps.documentos.views.administracion import *
from apps.documentos.views.galeria import *
from apps.documentos.views.generacion import *

app_name = "documentos"
urlpatterns = [
        path(
        "crear/",
        crear_plantilla_view,
        name="crear_plantilla"
    ),
    path(
        "biblioteca/",
        biblioteca_view,
        name="biblioteca"
    ),
    path(
        "generar/<int:plantilla_id>/",
        generar_documento_view,
        name="generar_documento"
    ),

    path(
        "generar/<int:plantilla_id>/clausulas/",
        seleccionar_clausulas_view,
        name="seleccionar_clausulas"
    ),
    path(
        "mis-documentos/",
        mis_documentos_view,
        name="mis_documentos"
    ),
    path(
        "mis-documentos/<int:documento_id>/pdf/",
        descargar_documento_pdf_view,
        name="descargar_documento_pdf"
    ),
    path(
        "descargar-y-volver/",
        descargar_y_volver_view,
        name="descargar_y_volver"
    ),
    path(
        "administracion/",
        panel_administracion_view,
        name="panel_administracion"
    ),
    path(
        "administracion//plantilla/<int:plantilla_id>/modificar/",
        modificar_plantilla_view,
        name="modificar_plantilla"
    ),
    path(
        "administracion//plantilla/<int:plantilla_id>/estado/",
        cambiar_estado_plantilla_view,
        name="cambiar_estado_plantilla"
    ),
    path(
        "administracion//plantilla/<int:plantilla_id>/editar/",
        editar_plantilla_view,
        name="editar_plantilla"
    ),
]