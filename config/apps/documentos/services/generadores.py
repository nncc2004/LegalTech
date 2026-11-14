
import re
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def generar_pdf(texto):
    """
    Genera un PDF sencillo a partir de texto plano.

    Args:
        texto (str): Texto ensamblado del documento.

    Returns:
        BytesIO: Archivo PDF generado en memoria.
    """

    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("El texto del documento no puede estar vacío.")

    # Crear archivo PDF en memoria.
    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title="Documento generado"
    )

    # Definir estilos.
    estilos = getSampleStyleSheet()

    estilo_parrafo = ParagraphStyle(
        "Documento",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceAfter=8
    )

    # Separar párrafos mediante líneas vacías.
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    parrafos = re.split(r"\n[ \t]*\n+", texto.strip())

    elementos = []

    for parrafo in parrafos:
        # Unir saltos de línea simples.
        parrafo = re.sub(r"\n", " ", parrafo).strip()

        if not parrafo:
            continue

        # Escapar caracteres especiales para ReportLab.
        parrafo = escape(parrafo)

        elementos.append(
            Paragraph(parrafo, estilo_parrafo)
        )

        elementos.append(Spacer(1, 4))

    # Construir PDF.
    documento.build(elementos)

    buffer.seek(0)

    return buffer
