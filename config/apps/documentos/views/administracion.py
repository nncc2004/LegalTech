
from django.shortcuts import render, redirect
from django.contrib import messages

from apps.documentos.forms import (
    PlantillaBaseForm,
    ContenidoPlantillaForm
)
from apps.core.decorators import solo_superusuario
from apps.documentos.services.deteccion import (
    generar_configuracion_inicial
)

from apps.documentos.services.editor import (
    generar_archivo_ctt
)

from apps.documentos.services.plantillas import (
    crear_plantilla
)

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