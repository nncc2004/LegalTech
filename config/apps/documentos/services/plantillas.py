from pathlib import Path
from copy import deepcopy

from django.core.files.base import ContentFile
from django.db import transaction

from apps.documentos.models import Plantilla


def _copiar_archivo(plantilla):
    """
    Lee el archivo de una plantilla y devuelve una copia
    independiente junto con su nombre original.
    """
    if not plantilla.archivo:
        raise ValueError("La plantilla no tiene un archivo asociado.")

    plantilla.archivo.open("rb")

    try:
        contenido = plantilla.archivo.read()
    finally:
        plantilla.archivo.close()

    nombre = Path(plantilla.archivo.name).name

    return nombre, ContentFile(contenido)


@transaction.atomic
def crear_plantilla(
    *,
    nombre,
    descripcion,
    categoria,
    archivo,
    campos,
    clausulas,
    validaciones,
    autor
):
    """
    Crea una plantilla nueva en estado de borrador.
    """

    return Plantilla.objects.create(
        nombre=nombre,
        descripcion=descripcion,
        categoria=categoria,
        archivo=archivo,
        campos=deepcopy(campos),
        clausulas=deepcopy(clausulas),
        validaciones=deepcopy(validaciones),
        autor=autor,
        publicada=True,
        activa=True,
        version=1
    )


@transaction.atomic
def duplicar_plantilla(plantilla, *, autor, nombre=None):
    """
    Crea una copia independiente de una plantilla existente.
    La copia comienza como borrador y como versión inicial.
    """

    copia = Plantilla(
        nombre=nombre or f"Copia de {plantilla.nombre}",
        descripcion=plantilla.descripcion,
        categoria=plantilla.categoria,
        campos=deepcopy(plantilla.campos),
        clausulas=deepcopy(plantilla.clausulas),
        validaciones=deepcopy(plantilla.validaciones),
        autor=autor,
        publicada=True,
        activa=True,
        version=1,
        plantilla_anterior=None
    )

    nombre_archivo, contenido = _copiar_archivo(plantilla)

    copia.archivo.save(nombre_archivo, contenido, save=False)
    copia.save()

    return copia


@transaction.atomic
def crear_nueva_version(plantilla, *, autor):
    """
    Crea una nueva versión de una plantilla publicada.
    Conserva la relación con la versión anterior.
    """

    if not plantilla.publicada:
        raise ValueError(
            "Solo se pueden crear nuevas versiones "
            "a partir de plantillas publicadas."
        )

    nueva_version = Plantilla(
        nombre=plantilla.nombre,
        descripcion=plantilla.descripcion,
        categoria=plantilla.categoria,
        campos=deepcopy(plantilla.campos),
        clausulas=deepcopy(plantilla.clausulas),
        validaciones=deepcopy(plantilla.validaciones),
        autor=autor,
        publicada=True,
        activa=True,
        version=plantilla.version + 1,
        plantilla_anterior=plantilla
    )

    nombre_archivo, contenido = _copiar_archivo(plantilla)

    nueva_version.archivo.save(
        nombre_archivo,
        contenido,
        save=False
    )

    nueva_version.save()

    return nueva_version





'''

# Crear y duplicar
def crear_plantilla():
    pass

def duplicar_plantilla():
    pass

# Versionamiento
def crear_nueva_version():
    pass

def actualizar_borrador():
    pass

def obtener_ultima_version():
    pass

# Publicación
def publicar_plantilla():
    pass

def despublicar_plantilla():
    pass

# Validaciones
def validar_modificacion():
    pass
    
    '''