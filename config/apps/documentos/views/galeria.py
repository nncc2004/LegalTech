from django.shortcuts import render
from django.db.models import Prefetch

from apps.documentos.models import Categoria, Plantilla


def biblioteca_view(request):
    """
    Muestra las plantillas publicadas y activas,
    agrupadas por categoría.
    """

    plantillas_publicadas = Plantilla.objects.filter(
        publicada=True,
        activa=True
    ).order_by("nombre")

    categorias = Categoria.objects.filter(
        plantillas__publicada=True,
        plantillas__activa=True
    ).distinct().prefetch_related(
        Prefetch(
            "plantillas",
            queryset=plantillas_publicadas
        )
    ).order_by("nombre")

    return render(
        request,
        "../templates/biblioteca.html",
        {
            "categorias": categorias
        }
    )