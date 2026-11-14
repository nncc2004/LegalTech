
from django.contrib import admin
from .models import Plantilla, Documento, Categoria


@admin.register(Plantilla)
class PlantillaAdmin(admin.ModelAdmin):

    list_display = (
        'nombre',
        'version',
        'publicada',
        'activa',
        'autor',
        'categoria',
        'fecha_creacion',
        'fecha_publicacion',
    )

    list_filter = (
        'publicada',
        'activa',
        'fecha_creacion',
        'categoria'
    )

    search_fields = (
        'nombre',
        'descripcion',
        'autor__username',
        'categoria__nombre',
    )

    readonly_fields = (
        'fecha_creacion',
    )

    autocomplete_fields = (
        'autor',
        'plantilla_anterior',
        'categoria',
    )

    fieldsets = (
        ('Información general', {
            'fields': (
                'nombre',
                'descripcion',
                'autor',
                'categoria',
            )
        }),
        ('Contenido', {
            'fields': (
                'archivo',
                'campos',
                'clausulas',
                'validaciones',
            )
        }),
        ('Publicación y versiones', {
            'fields': (
                'publicada',
                'activa',
                'version',
                'plantilla_anterior',
                'fecha_publicacion',
            )
        }),
        ('Fechas', {
            'fields': (
                'fecha_creacion',
            )
        }),
    )


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'plantilla',
        'usuario',
        'fecha_creacion',
    )

    list_filter = (
        'fecha_creacion',
        'plantilla',
    )

    search_fields = (
        'plantilla__nombre',
        'usuario__username',
    )

    readonly_fields = (
        'fecha_creacion',
    )

    autocomplete_fields = (
        'usuario',
        'plantilla',
    )

    fieldsets = (
        ('Información general', {
            'fields': (
                'usuario',
                'plantilla',
            )
        }),
        ('Datos ingresados', {
            'fields': (
                'campos',
            )
        }),
        ('Fecha', {
            'fields': (
                'fecha_creacion',
            )
        }),
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)