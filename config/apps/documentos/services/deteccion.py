
import re


PATRON_MARCADORES = re.compile(
    r"\{\{\s*([a-zA-Z][a-zA-Z0-9_]*)\s*\}\}"
)

PATRON_BLOQUES = re.compile(
    r"\{\{\s*(?P<tipo>[#/])\s*"
    r"(?P<identificador>clausula_[a-zA-Z][a-zA-Z0-9_]*)"
    r"\s*\}\}"
)


def _extraer_bloques_clausula(texto):
    """
    Extrae los bloques de cláusulas y su contenido.

    Rechaza bloques sin cerrar, cierres incorrectos,
    bloques anidados e identificadores duplicados.
    """

    clausulas = []
    pila = []
    identificadores = set()

    for coincidencia in PATRON_BLOQUES.finditer(texto):
        tipo = coincidencia.group("tipo")
        identificador = coincidencia.group("identificador")

        if tipo == "#":
            if pila:
                raise ValueError(
                    "No se permiten cláusulas anidadas."
                )

            if identificador in identificadores:
                raise ValueError(
                    f"La cláusula '{identificador}' está repetida."
                )

            identificadores.add(identificador)

            pila.append({
                "identificador": identificador,
                "inicio": coincidencia.end()
            })

        else:
            if not pila:
                raise ValueError(
                    f"Existe un cierre sin apertura para '{identificador}'."
                )

            bloque = pila.pop()

            if bloque["identificador"] != identificador:
                raise ValueError(
                    f"El cierre de '{identificador}' no corresponde "
                    f"a la cláusula '{bloque['identificador']}'."
                )

            contenido = texto[bloque["inicio"]:coincidencia.start()]

            clausulas.append({
                "identificador": identificador,
                "contenido": contenido.strip()
            })

    if pila:
        identificador = pila[-1]["identificador"]
        raise ValueError(
            f"La cláusula '{identificador}' no tiene cierre."
        )

    return clausulas


def detectar_marcadores(texto):
    """
    Detecta campos dinámicos y bloques de cláusulas.
    Conserva el orden de aparición.
    """

    if not isinstance(texto, str):
        raise TypeError("El contenido debe ser texto.")

    bloques = _extraer_bloques_clausula(texto)

    identificadores_campos = []

    for identificador in PATRON_MARCADORES.findall(texto):
        if identificador.startswith("clausula_"):
            raise ValueError(
                "Las cláusulas deben utilizar bloques: "
                "{{#clausula_nombre}} ... {{/clausula_nombre}}."
            )

        if identificador not in identificadores_campos:
            identificadores_campos.append(identificador)

    return {
        "campos": identificadores_campos,
        "clausulas": [
            bloque["identificador"] for bloque in bloques
        ],
        "contenido_clausulas": bloques
    }


def validar_marcadores(texto):
    """
    Comprueba que los marcadores y bloques estén bien formados.
    """

    if not isinstance(texto, str):
        raise TypeError("El contenido debe ser texto.")

    marcadores = detectar_marcadores(texto)

    texto_limpio = PATRON_MARCADORES.sub("", texto)
    texto_limpio = PATRON_BLOQUES.sub("", texto_limpio)

    if "{{" in texto_limpio or "}}" in texto_limpio:
        raise ValueError(
            "Se encontraron marcadores mal formados. "
            "Revisa las expresiones entre llaves."
        )

    return marcadores


def generar_configuracion_inicial(texto):
    """
    Genera la configuración inicial de campos y cláusulas
    a partir del contenido de la plantilla.
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

    for bloque in marcadores["contenido_clausulas"]:
        identificador = bloque["identificador"]
        etiqueta = identificador.replace("_", " ").capitalize()

        clausulas.append({
            "identificador": identificador,
            "etiqueta": etiqueta,
            "condicion": None,
            "contenido": bloque["contenido"]
        })

    return {
        "campos": campos,
        "clausulas": clausulas
    }
