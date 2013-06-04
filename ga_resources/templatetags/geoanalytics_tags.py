from django import template
from lxml import etree
from django.conf import settings
import importlib

# _page_mapping = importlib.import_module(settings.SUBPAGE_MAPPING_MODULE)

_page_mapping = object()
_page_mapping.pages = {

}

_page_mapping.contenttypes = {
    'dataresource' : [
        ("Page", "mezzanine.pages.models", "RichTextPage", {}),
        ("Styled Map", "ga_resources.models", "WMS", {}),
        ("Style", "ga_resources.models", "Style", {}),
    ]
}

register = template.Library()

class SubpageNode(template.Node):
    def render(self, context):
        page = context['page']
        if page.slug in _page_mapping.pages:
            pass
        elif page.content_model in _page_mapping.contenttypes:
            pass

@register.tag("subpage_button")
def do_add_subpage(parser, token):
    return SubpageNode()