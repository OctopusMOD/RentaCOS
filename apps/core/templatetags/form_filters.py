from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Agrega clases CSS a un campo de formulario Django sin perder las clases existentes.
    Uso en template: {{ form.campo|add_class:"form-control mb-2" }}
    """
    attrs = field.field.widget.attrs.copy()
    existing_classes = attrs.get('class', '')
    classes = f"{existing_classes} {css_class}".strip()
    attrs['class'] = classes
    return field.as_widget(attrs=attrs)