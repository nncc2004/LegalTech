from django.shortcuts import render
import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

from apps.asistente.services.recomendador import recomendar_plantilla


@login_required
@require_POST
@csrf_protect
def recomendar_plantilla_view(request):
    """
    Recibe la descripción del usuario y devuelve
    una recomendación de plantilla.
    """

    try:
        datos = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "La solicitud contiene JSON inválido."},
            status=400
        )

    descripcion = datos.get("descripcion")

    if not isinstance(descripcion, str) or not descripcion.strip():
        return JsonResponse(
            {"error": "Debes proporcionar una descripción válida."},
            status=400
        )

    try:
        resultado = recomendar_plantilla(descripcion)

        return JsonResponse({
            "success": True,
            "recomendacion": resultado
        })

    except ValueError as error:
        return JsonResponse(
            {"error": str(error)},
            status=400
        )

    except Exception:
        return JsonResponse(
            {
                "error": (
                    "No fue posible obtener una recomendación. "
                    "Puedes seleccionar una plantilla manualmente."
                )
            },
            status=503
        )