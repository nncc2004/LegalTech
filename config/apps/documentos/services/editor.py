# apps/documentos/services/editor.py

from django.core.files.base import ContentFile
from django.utils.text import slugify

from apps.documentos.services.deteccion import validar_marcadores


def generar_archivo_ctt(texto, nombre):
    """
    Convierte el texto jurídico en un archivo .ctt.
    Conserva el contenido y los marcadores originales.
    """

    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("El contenido no puede estar vacío.")

    nombre_archivo = slugify(nombre)

    if not nombre_archivo:
        raise ValueError("El nombre de la plantilla no es válido.")

    contenido = texto.encode("utf-8")

    return ContentFile(
        contenido,
        name=f"{nombre_archivo}.ctt"
    )



def validar_configuracion(texto, campos, clausulas):
    """
    Comprueba que los campos y cláusulas del texto
    tengan una configuración correspondiente.

    También verifica que el contenido configurado de cada
    cláusula coincida con el bloque del archivo .ctt.
    """

    marcadores = validar_marcadores(texto)

    identificadores_campos = set(campos.keys())

    clausulas_configuradas = {
        clausula["identificador"]: clausula
        for clausula in clausulas
    }

    detectados_campos = set(marcadores["campos"])
    detectadas_clausulas = set(marcadores["clausulas"])

    errores = []

    # Comprobar campos.
    campos_sin_configurar = detectados_campos - identificadores_campos
    campos_sin_marcador = identificadores_campos - detectados_campos

    if campos_sin_configurar:
        errores.append(
            f"Campos sin configurar: {sorted(campos_sin_configurar)}"
        )

    if campos_sin_marcador:
        errores.append(
            f"Campos configurados que no aparecen en el texto: "
            f"{sorted(campos_sin_marcador)}"
        )

    # Comprobar identificadores de cláusulas.
    clausulas_sin_configurar = (
        detectadas_clausulas - set(clausulas_configuradas)
    )

    clausulas_sin_marcador = (
        set(clausulas_configuradas) - detectadas_clausulas
    )

    if clausulas_sin_configurar:
        errores.append(
            f"Cláusulas sin configurar: {sorted(clausulas_sin_configurar)}"
        )

    if clausulas_sin_marcador:
        errores.append(
            f"Cláusulas configuradas que no aparecen en el texto: "
            f"{sorted(clausulas_sin_marcador)}"
        )

    # Comprobar que el contenido de las cláusulas coincida.
    for bloque in marcadores["contenido_clausulas"]:
        identificador = bloque["identificador"]
        clausula = clausulas_configuradas.get(identificador)

        if clausula is None:
            continue

        contenido_texto = bloque["contenido"].strip()
        contenido_configurado = clausula.get("contenido", "").strip()

        if contenido_texto != contenido_configurado:
            errores.append(
                f"El contenido configurado de la cláusula "
                f"'{identificador}' no coincide con el archivo .ctt."
            )

    if errores:
        raise ValueError("\n".join(errores))

    return True

'''
def validar_configuracion(texto, campos, clausulas):
    """
    Comprueba que todos los marcadores del texto
    tengan una configuración correspondiente.

    campos: diccionario cuyas claves son identificadores.
    clausulas: lista de diccionarios con una clave
               'identificador'.
    """

    marcadores = validar_marcadores(texto)

    identificadores_campos = set(campos.keys())

    identificadores_clausulas = {
        clausula["identificador"]
        for clausula in clausulas
    }

    detectados_campos = set(marcadores["campos"])
    detectadas_clausulas = set(marcadores["clausulas"])

    errores = []

    campos_sin_configurar = detectados_campos - identificadores_campos
    campos_sin_marcador = identificadores_campos - detectados_campos

    clausulas_sin_configurar = (
        detectadas_clausulas - identificadores_clausulas
    )
    clausulas_sin_marcador = (
        identificadores_clausulas - detectadas_clausulas
    )

    if campos_sin_configurar:
        errores.append(
            f"Campos sin configurar: {sorted(campos_sin_configurar)}"
        )

    if campos_sin_marcador:
        errores.append(
            f"Campos configurados que no aparecen en el texto: "
            f"{sorted(campos_sin_marcador)}"
        )

    if clausulas_sin_configurar:
        errores.append(
            f"Cláusulas sin configurar: {sorted(clausulas_sin_configurar)}"
        )

    if clausulas_sin_marcador:
        errores.append(
            f"Cláusulas configuradas que no aparecen en el texto: "
            f"{sorted(clausulas_sin_marcador)}"
        )

    if errores:
        raise ValueError("\n".join(errores))

    return True

'''

