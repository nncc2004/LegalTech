import re


PATRON_MARCADORES = re.compile(
    r"\{\{\s*([a-zA-Z][a-zA-Z0-9_]*)\s*\}\}"
)


def detectar_marcadores(texto):
    """
    Detecta los marcadores del texto y los clasifica
    en campos dinámicos y cláusulas.

    Devuelve identificadores únicos, conservando
    el orden de aparición.
    """

    if not isinstance(texto, str):
        raise TypeError("El contenido debe ser texto.")

    identificadores = list(dict.fromkeys(
        PATRON_MARCADORES.findall(texto)
    ))

    campos = []
    clausulas = []

    for identificador in identificadores:
        if identificador.startswith("clausula_"):
            clausulas.append(identificador)
        else:
            campos.append(identificador)

    return {
        "campos": campos,
        "clausulas": clausulas
    }


def validar_marcadores(texto):
    """
    Comprueba si existen marcadores mal formados
    o llaves sin correspondencia.
    """

    if not isinstance(texto, str):
        raise TypeError("El contenido debe ser texto.")

    marcadores = detectar_marcadores(texto)
    texto_limpio = PATRON_MARCADORES.sub("", texto)

    if "{{" in texto_limpio or "}}" in texto_limpio:
        raise ValueError(
            "Se encontraron marcadores mal formados. "
            "Revisa las expresiones entre llaves."
        )

    return marcadores



def generar_configuracion_inicial(texto):
    """
    Genera una configuración inicial de campos y cláusulas
    a partir de los marcadores encontrados en el texto.

    Los valores generados son provisionales y deberán
    ser revisados por el profesional jurídico.
    """

    marcadores = validar_marcadores(texto)

    campos = {}

    for identificador in marcadores["campos"]:
        etiqueta = identificador.replace("_", " ").capitalize()

        campos[identificador] = {
            "etiqueta": etiqueta,
            "tipo": "texto",
            "obligatorio": True
        }

    clausulas = []

    for identificador in marcadores["clausulas"]:
        etiqueta = identificador.replace("_", " ").capitalize()

        clausulas.append({
            "identificador": identificador,
            "etiqueta": etiqueta,
            "condicion": None,
            "contenido": ""
        })

    return {
        "campos": campos,
        "clausulas": clausulas
    }