from django.db import models
from django.conf import settings

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Plantilla(models.Model):

    # Identificación
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()

    # Archivo con el texto base (.ctt)
    archivo = models.FileField(upload_to='plantillas/')

    # Definición de la plantilla
    campos = models.JSONField(default=dict, null=True, blank=True)
    clausulas = models.JSONField(default=list, null=True, blank=True)
    validaciones = models.JSONField(default=list, null=True, blank=True)

    # Publicación y versiones
    publicada = models.BooleanField(default=True)
    activa = models.BooleanField(default=True)

    version = models.PositiveIntegerField(default=1)

    plantilla_anterior = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='versiones'
    )

    # Autoría y fechas
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='plantillas_creadas'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_publicacion = models.DateTimeField(
        null=True,
        blank=True
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='plantillas',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.nombre} (v{self.version})"


class Documento(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_generados'
    )

    plantilla = models.ForeignKey(
        Plantilla,
        on_delete=models.PROTECT,
        related_name='documentos'
    )

    campos = models.JSONField(default=dict)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Documento {self.id} - {self.plantilla.nombre}"


