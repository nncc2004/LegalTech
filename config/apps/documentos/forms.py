from django import forms

from apps.documentos.models import Categoria
from apps.documentos.services.deteccion import validar_marcadores


class PlantillaBaseForm(forms.Form):
    """
    Formulario para los datos generales de una plantilla.
    """

    nombre = forms.CharField(
        label="Nombre de la plantilla",
        max_length=150,
        widget=forms.TextInput(attrs={
            "placeholder": "Ej: Contrato de arrendamiento"
        })
    )

    descripcion = forms.CharField(
        label="Descripción",
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Describe brevemente la plantilla..."
        })
    )

    categoria = forms.ModelChoiceField(
        label="Categoría",
        queryset=Categoria.objects.all(),
        empty_label="Selecciona una categoría"
    )


class ContenidoPlantillaForm(forms.Form):
    """
    Formulario para recibir el texto jurídico de la plantilla.
    """

    texto = forms.CharField(
        label="Contenido jurídico",
        widget=forms.Textarea(attrs={
            "rows": 20,
            "placeholder": (
                "Escribe o pega aquí el contenido jurídico...\n\n"
                "Utiliza {{nombre_campo}} para insertar campos dinámicos.\n"
                "Utiliza {{clausula_nombre}} para insertar cláusulas."
            )
        })
    )

    def clean_texto(self):
        """
        Valida la sintaxis de los marcadores del documento.
        """

        texto = self.cleaned_data["texto"]

        try:
            validar_marcadores(texto)
        except ValueError as error:
            raise forms.ValidationError(str(error))

        return texto


class PlantillaEdicionForm(forms.Form):

    nombre = forms.CharField(
        label="Nombre de la plantilla",
        max_length=150
    )

    descripcion = forms.CharField(
        label="Descripción",
        widget=forms.Textarea(attrs={"rows": 3})
    )

    categoria = forms.ModelChoiceField(
        label="Categoría",
        queryset=Categoria.objects.all()
    )

    texto = forms.CharField(
        label="Contenido jurídico",
        widget=forms.Textarea(attrs={"rows": 20})
    )