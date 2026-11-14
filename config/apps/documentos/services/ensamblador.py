

import re

from apps.documentos.services.deteccion import (
    PATRON_MARCADORES,
    validar_marcadores,
)


PATRON_BLOQUES_CLAUSULA = re.compile(
    r"\{\{\s*#\s*(clausula_[a-zA-Z][a-zA-Z0-9_]*)\s*\}\}"
    r"(.*?)"
    r"\{\{\s*/\s*\1\s*\}\}",
    re.DOTALL
)


def normalizar_saltos_linea(texto):
    # Unificar los formatos de salto de línea.
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")

    # Convertir líneas vacías consecutivas en una separación.
    texto = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)*", "\n\n", texto)

    # Unir líneas que no están separadas por una línea vacía.
    texto = re.sub(r"(?<!\n)\n(?!\n)", " ", texto)

    return texto.strip()


def ensamblar_documento(documento):
    """
    Ensambla el texto de una plantilla utilizando los datos
    y las cláusulas seleccionadas de un Documento.

    Retorna:
        str: Texto completo del documento ensamblado.

    Raises:
        ValueError: Si faltan datos, existen marcadores inválidos
                    o hay problemas con la configuración.
    """

    plantilla = documento.plantilla

    # 1. Recuperar los datos del documento.
    datos = documento.campos

    campos = datos.get("campos", {})
    clausulas_seleccionadas = datos.get("clausulas", {})

    # 2. Recuperar el texto original de la plantilla.
    if not plantilla.archivo:
        raise ValueError("La plantilla no tiene un archivo asociado.")

    with plantilla.archivo.open("rb") as archivo:
        texto = archivo.read().decode("utf-8")
        texto = normalizar_saltos_linea(texto)

    validar_marcadores(texto)

    # 3. Construir un diccionario de cláusulas configuradas.
    clausulas_configuradas = {
        clausula["identificador"]: clausula
        for clausula in plantilla.clausulas
    }

    # 4. Comprobar que no existan selecciones desconocidas.
    clausulas_desconocidas = (
        set(clausulas_seleccionadas) - set(clausulas_configuradas)
    )

    if clausulas_desconocidas:
        raise ValueError(
            f"Cláusulas desconocidas: {clausulas_desconocidas}"
        )

    # 5. Procesar los bloques de cláusulas.
    def reemplazar_bloque(coincidencia):
        identificador = coincidencia.group(1)

        clausula = clausulas_configuradas.get(identificador)

        if clausula is None:
            raise ValueError(
                f"No existe configuración para la cláusula "
                f"'{identificador}'."
            )

        # Si no fue seleccionada, se elimina el bloque completo.
        if not clausulas_seleccionadas.get(identificador, False):
            return ""

        # Recuperar el contenido directamente del archivo .ctt.
        contenido = coincidencia.group(2)
        contenido = normalizar_saltos_linea(contenido)

        if not contenido:
            raise ValueError(
                f"La cláusula '{identificador}' no tiene contenido."
            )

        return contenido

    texto = PATRON_BLOQUES_CLAUSULA.sub(
        reemplazar_bloque,
        texto
    )

    # 6. Reemplazar los campos dinámicos.
    def reemplazar_campo(coincidencia):
        identificador = coincidencia.group(1)

        if identificador.startswith("clausula_"):
            raise ValueError(
                "Se encontró un marcador de cláusula fuera "
                "de un bloque válido."
            )

        if identificador not in campos:
            raise ValueError(
                f"No se proporcionó un valor para el campo "
                f"'{identificador}'."
            )

        valor = campos[identificador]

        if valor is None:
            return ""

        return str(valor)

    texto_final = PATRON_MARCADORES.sub(
        reemplazar_campo,
        texto
    )

    return texto_final


'''
from apps.documentos.services.deteccion import (
    PATRON_MARCADORES,
    validar_marcadores,
)


import re


def normalizar_saltos_linea(texto):
    # Unificar los formatos de salto de línea.
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")

    # Convertir líneas vacías consecutivas en una separación.
    texto = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)*", "\n\n", texto)

    # Unir líneas que no están separadas por una línea vacía.
    texto = re.sub(r"(?<!\n)\n(?!\n)", " ", texto)

    return texto.strip()

def ensamblar_documento(documento):
    """
    Ensambla el texto de una plantilla utilizando los datos
    y las cláusulas seleccionadas de un Documento.

    Retorna:
        str: Texto completo del documento ensamblado.

    Raises:
        ValueError: Si faltan datos, existen marcadores inválidos
                    o hay problemas con la configuración.
    """

    plantilla = documento.plantilla

    # 1. Recuperar los datos del documento.
    datos = documento.campos

    campos = datos.get("campos", {})
    clausulas_seleccionadas = datos.get("clausulas", {})

    # 2. Recuperar el texto original de la plantilla.
    if not plantilla.archivo:
        raise ValueError("La plantilla no tiene un archivo asociado.")

    with plantilla.archivo.open("rb") as archivo:
        texto = archivo.read().decode("utf-8")
        texto = normalizar_saltos_linea(texto)

    validar_marcadores(texto)

    # 3. Construir un diccionario de cláusulas.
    clausulas_configuradas = {
        clausula["identificador"]: clausula
        for clausula in plantilla.clausulas
    }

    # 4. Comprobar que no existan selecciones desconocidas.
    clausulas_desconocidas = (
        set(clausulas_seleccionadas) - set(clausulas_configuradas)
    )

    if clausulas_desconocidas:
        raise ValueError(
            f"Cláusulas desconocidas: {clausulas_desconocidas}"
        )

    # 5. Reemplazar los marcadores.
    def reemplazar_marcador(coincidencia):
        identificador = coincidencia.group(1)

        # Marcador de cláusula.
        if identificador.startswith("clausula_"):

            clausula = clausulas_configuradas.get(identificador)

            if clausula is None:
                raise ValueError(
                    f"No existe configuración para la cláusula "
                    f"'{identificador}'."
                )

            # Si no fue seleccionada, se omite.
            if not clausulas_seleccionadas.get(identificador, False):
                return ""

            contenido = clausula.get("contenido", "")
            contenido = normalizar_saltos_linea(contenido)

            if not contenido.strip():
                raise ValueError(
                    f"La cláusula '{identificador}' no tiene contenido."
                )

            # Reemplazar posibles marcadores de campos dentro
            # del contenido de la cláusula.
            return PATRON_MARCADORES.sub(
                reemplazar_campo,
                contenido
            )

        # Marcador de campo.
        return reemplazar_campo(coincidencia)

    def reemplazar_campo(coincidencia):
        identificador = coincidencia.group(1)

        if identificador.startswith("clausula_"):
            raise ValueError(
                "No se permiten cláusulas anidadas."
            )

        if identificador not in campos:
            raise ValueError(
                f"No se proporcionó un valor para el campo "
                f"'{identificador}'."
            )

        valor = campos[identificador]

        if valor is None:
            return ""

        return str(valor)

    texto_final = PATRON_MARCADORES.sub(
        reemplazar_marcador,
        texto
    )

    return texto_final
'''