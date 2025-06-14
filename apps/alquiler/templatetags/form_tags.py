from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    attrs = field.field.widget.attrs
    existing_classes = attrs.get('class', '')
    classes = f"{existing_classes} {css_class}".strip()
    return field.as_widget(attrs={"class": classes})