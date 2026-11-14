from django import forms


def generar_formulario(plantilla):
    """
    Genera dinámicamente un formulario Django
    utilizando la configuración JSON de una plantilla.
    """

    campos_configurados = plantilla.campos

    class FormularioDinamico(forms.Form):
        pass

    tipos_campos = {
        "texto": forms.CharField,
        "numero": forms.IntegerField,
        "decimal": forms.DecimalField,
        "fecha": forms.DateField,
        "correo": forms.EmailField,
        "rut": forms.CharField,
        "booleano": forms.BooleanField,
    }

    for identificador, configuracion in campos_configurados.items():

        tipo = configuracion.get("tipo", "texto")
        etiqueta = configuracion.get("etiqueta", identificador)
        obligatorio = configuracion.get("obligatorio", True)

        clase_campo = tipos_campos.get(tipo)

        if clase_campo is None:
            raise ValueError(
                f"Tipo de campo no soportado: {tipo}"
            )

        argumentos = {
            "label": etiqueta,
            "required": obligatorio,
        }

        if tipo == "fecha":
            argumentos["widget"] = forms.DateInput(
                attrs={"type": "date"}
            )

        elif tipo == "booleano":
            argumentos["required"] = False

        FormularioDinamico.base_fields[identificador] = clase_campo(
            **argumentos
        )

    return FormularioDinamico


def generar_formulario_clausulas(plantilla):
    clausulas_configuradas = plantilla.clausulas

    class FormularioClausulas(forms.Form):
        pass

    for clausula in clausulas_configuradas:
        identificador = clausula["identificador"]
        etiqueta = clausula.get("etiqueta", identificador)

        FormularioClausulas.base_fields[identificador] = (
            forms.BooleanField(
                label=etiqueta,
                required=False
            )
        )

    return FormularioClausulas
