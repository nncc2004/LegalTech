from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from apps.documentos.models import Plantilla, Documento
from apps.documentos.services.formularios import *

from django.contrib.auth.decorators import login_required
from apps.documentos.services.ensamblador import ensamblar_documento


from django.http import HttpResponse
from django.utils.text import slugify

from apps.documentos.services.generadores import generar_pdf


def generar_documento_view(request, plantilla_id):
    plantilla = get_object_or_404(
        Plantilla,
        id=plantilla_id,
        activa=True
    )

    Formulario = generar_formulario(plantilla)

    if request.method == "POST":
        formulario = Formulario(request.POST)

        if formulario.is_valid():
            # Guardar temporalmente los datos generales en la sesión.
            request.session["documento_temporal"] = {
                "plantilla_id": plantilla.id,
                "campos": formulario.cleaned_data
            }

            # Continuar al formulario de cláusulas.
            return redirect(
                "documentos:seleccionar_clausulas",
                plantilla_id=plantilla.id
            )

    else:
        formulario = Formulario()

    return render(request, "../templates/generar_documento.html", {
        "plantilla": plantilla,
        "formulario": formulario
    })



def seleccionar_clausulas_view(request, plantilla_id):

    # Recuperar los datos temporales de la sesión.
    datos_temporales = request.session.get("documento_temporal")

    # Comprobar que se haya completado el primer formulario.
    if not datos_temporales or datos_temporales["plantilla_id"] != plantilla_id:
        messages.error(request, "Primero debes completar los datos generales.")
        return redirect(
            "documentos:generar_documento",
            plantilla_id=plantilla_id
        )

    plantilla = get_object_or_404(
        Plantilla,
        id=plantilla_id,
        activa=True
    )

    # Si no existen cláusulas, guardar directamente.
    if not plantilla.clausulas:
        return guardar_documento(request, plantilla, datos_temporales, {})

    Formulario = generar_formulario_clausulas(plantilla)

    if request.method == "POST":
        formulario = Formulario(request.POST)

        if formulario.is_valid():
            return guardar_documento(
                request,
                plantilla,
                datos_temporales,
                formulario.cleaned_data
            )

    else:
        formulario = Formulario()

    return render(request, "../templates/seleccionar_clausulas.html", {
        "plantilla": plantilla,
        "formulario": formulario
    })


def guardar_documento(request, plantilla, datos_temporales, clausulas):

    usuario = request.user if request.user.is_authenticated else None

    documento = Documento.objects.create(
        usuario=usuario,
        plantilla=plantilla,
        campos={
            "campos": datos_temporales["campos"],
            "clausulas": clausulas
        }
    )

    request.session.pop("documento_temporal", None)

    # Identificar el documento recién creado para la descarga.
    request.session["documento_descarga_id"] = documento.id

    return redirect("documentos:descargar_y_volver")

def descargar_y_volver_view(request):

    documento_id = request.session.get("documento_descarga_id")

    if not documento_id:
        return redirect("documentos:biblioteca")

    documento = get_object_or_404(
        Documento,
        id=documento_id
    )

    # Comprobar propiedad del documento.
    if documento.usuario_id:
        if not request.user.is_authenticated or documento.usuario_id != request.user.id:
            return redirect("documentos:biblioteca")

    texto = ensamblar_documento(documento)
    pdf = generar_pdf(texto)

    import base64

    pdf_base64 = base64.b64encode(pdf.getvalue()).decode("ascii")

    request.session.pop("documento_descarga_id", None)

    return render(request, "../templates/descargar_y_volver.html", {
        "pdf_base64": pdf_base64,
        "nombre_archivo": slugify(documento.plantilla.nombre)
    })

@login_required
def mis_documentos_view(request):

    documentos = request.user.documentos_generados.select_related(
        "plantilla"
    ).order_by("-fecha_creacion")

    return render(request, "../templates/mis_documentos.html", {
        "documentos": documentos
    })

@login_required
def descargar_documento_pdf_view(request, documento_id):

    try:
        documento = get_object_or_404(
            request.user.documentos_generados.select_related("plantilla"),
            id=documento_id
        )

        texto = ensamblar_documento(documento)
        pdf = generar_pdf(texto)

        nombre_archivo = slugify(documento.plantilla.nombre)

        respuesta = HttpResponse(
            pdf.getvalue(),
            content_type="application/pdf"
        )

        respuesta["Content-Disposition"] = (
            f'attachment; filename="{nombre_archivo}.pdf"'
        )

        return respuesta

    except Exception:
        logger.exception("Error al descargar PDF del documento %s", documento_id)
        raise