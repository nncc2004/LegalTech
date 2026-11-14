
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from apps.documentos.models import Plantilla
from apps.documentos.forms import (
    PlantillaBaseForm,
    ContenidoPlantillaForm,
    PlantillaEdicionForm
)
from apps.core.decorators import solo_superusuario
from apps.documentos.services.deteccion import (
    generar_configuracion_inicial,
    validar_marcadores
)

from apps.documentos.services.editor import generar_archivo_ctt
from apps.documentos.services.plantillas import (
    crear_plantilla, duplicar_plantilla
)

from django.views.decorators.http import require_POST


@solo_superusuario
def crear_plantilla_view(request):
    """
    Permite al profesional jurídico crear una plantilla.

    Recibe los datos generales y el texto jurídico,
    detecta sus marcadores y genera la configuración inicial.
    """

    if request.method == "POST":

        formulario_base = PlantillaBaseForm(request.POST)
        formulario_contenido = ContenidoPlantillaForm(request.POST)

        if formulario_base.is_valid() and formulario_contenido.is_valid():

            datos = formulario_base.cleaned_data
            texto = formulario_contenido.cleaned_data["texto"]

            try:
                # Detectar campos y cláusulas
                configuracion = generar_configuracion_inicial(texto)

                # Generar archivo .ctt
                archivo = generar_archivo_ctt(
                    texto,
                    datos["nombre"]
                )

                # Crear plantilla en la base de datos
                plantilla = crear_plantilla(
                    nombre=datos["nombre"],
                    descripcion=datos["descripcion"],
                    categoria=datos["categoria"],
                    archivo=archivo,
                    campos=configuracion["campos"],
                    clausulas=configuracion["clausulas"],
                    validaciones=[],
                    autor=request.user
                )

                messages.success(
                    request,
                    "La plantilla se creó correctamente."
                )

                return redirect("documentos:crear_plantilla")

            except (ValueError, OSError) as error:
                messages.error(request, str(error))

    else:
        formulario_base = PlantillaBaseForm()
        formulario_contenido = ContenidoPlantillaForm()

    return render(
        request,
        "../templates/crear_plantilla.html",
        {
            "formulario_base": formulario_base,
            "formulario_contenido": formulario_contenido
        }
    )



@solo_superusuario
def panel_administracion_view(request):
    plantillas = Plantilla.objects.select_related(
        "categoria"
    ).order_by("nombre")

    return render(
        request,
        "../templates/panel.html",
        {"plantillas": plantillas}
    )



@solo_superusuario
def modificar_plantilla_view(request, plantilla_id):
    plantilla = get_object_or_404(Plantilla, id=plantilla_id)

    if request.method == "POST":
        copia = duplicar_plantilla(
            plantilla,
            autor=request.user
        )

        return redirect("documentos:editar_plantilla", plantilla_id=copia.id)

    return redirect("documentos:panel_administracion")


@solo_superusuario
@require_POST
def cambiar_estado_plantilla_view(request, plantilla_id):
    plantilla = get_object_or_404(Plantilla, id=plantilla_id)

    plantilla.activa = not plantilla.activa
    plantilla.save(update_fields=["activa"])

    return redirect("documentos:panel_administracion")

@solo_superusuario
def editar_plantilla_view(request, plantilla_id):

    plantilla = get_object_or_404(Plantilla, id=plantilla_id)

    if request.method == "POST":

        formulario = PlantillaEdicionForm(request.POST)

        if formulario.is_valid():

            datos = formulario.cleaned_data
            texto = datos["texto"]

            try:
                # Validar sintaxis de los marcadores
                validar_marcadores(texto)

                # Detectar automáticamente campos y cláusulas
                configuracion = generar_configuracion_inicial(texto)

                # Generar nuevo archivo .ctt
                archivo = generar_archivo_ctt(
                    texto,
                    datos["nombre"]
                )

                # Actualizar la copia
                plantilla.nombre = datos["nombre"]
                plantilla.descripcion = datos["descripcion"]
                plantilla.categoria = datos["categoria"]
                plantilla.campos = configuracion["campos"]
                plantilla.clausulas = configuracion["clausulas"]
                plantilla.validaciones = []

                plantilla.archivo.save(
                    archivo.name,
                    archivo,
                    save=False
                )

                plantilla.save()

                messages.success(
                    request,
                    "La plantilla se actualizó correctamente."
                )

                return redirect("documentos:panel_administracion")

            except (ValueError, OSError) as error:
                messages.error(request, str(error))

    else:

        # Leer el archivo .ctt en UTF-8
        plantilla.archivo.open("rb")

        try:
            texto = plantilla.archivo.read().decode("utf-8")
        finally:
            plantilla.archivo.close()

        formulario = PlantillaEdicionForm(initial={
            "nombre": plantilla.nombre,
            "descripcion": plantilla.descripcion,
            "categoria": plantilla.categoria,
            "texto": texto
        })

    return render(
        request,
        "../templates/editar_plantilla.html",
        {
            "formulario": formulario,
            "plantilla": plantilla
        }
    )
