from django import template

register = template.Library()

@register.filter
def has_certificate(certificates, module):
    """Check if a module has a certificate in the certificates queryset"""
    return certificates.filter(module=module).exists() 