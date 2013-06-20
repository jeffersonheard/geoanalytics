from django import template
from lxml import etree
from django.conf import settings
import importlib
from collections import namedtuple

# _page_mapping = importlib.import_module(settings.SUBPAGE_MAPPING_MODULE)

_pages = {

}

_contenttypes = {
    'catalogpage' : [
        ("Catalog Page", "ga_resources.models", "CatalogPage"),
        ("Data Resource", "ga_resources.models", "DataResource"),
        ("Styled Map", "ga_resources.models", "RenderedLayer"),
        ("Style", "ga_resources.models", "Style")
    ],
    'dataresource' : [
        ("Page", "mezzanine.pages.models", "RichTextPage"),
        ("Styled Map", "ga_resources.models", "RenderedLayer"),
        ("Style", "ga_resources.models", "Style"),
    ]
}

register = template.Library()

class SubpageNode(template.Node):
    def render(self, context):
        page = context['page']
        if page.slug in _pages:
            div = etree.Element('div', attrib={'class' : 'btn-group'})
            a = etree.SubElement(div, 'a', attrib={
                'href' : '#',
                'data-toggle' : 'dropdown',
                'class' : 'btn dropdown-toggle'
            })
            a.append(etree.Element("span", attrib={'class': 'caret'}))
            a.text = 'Create new '
            ul = etree.SubElement(div, 'ul', attrib={
                "class" : "dropdown-menu"
            })
            for title, package, model in _pages[page.slug]:
                li = etree.SubElement(ul, "li")
                a = etree.SubElement(li, 'a', attrib={
                    'href' : '/ga_resources/createpage/?module={module}&classname={classname}&parent={slug}'.format(
                        module=package,
                        classname=model,
                        slug=page.slug)
                })
                a.text = title

        elif page.content_model in _contenttypes:
            div = etree.Element('div', attrib={'class' : 'btn-group'})
            a = etree.SubElement(div, 'button', attrib={
                #'href': '#',
                'data-toggle': 'dropdown',
                'class': 'btn dropdown-toggle'
            })
            a.text = 'Create new '
            a.append(etree.Element("span", attrib={'class' : 'caret'}))
            ul = etree.SubElement(div, 'ul', attrib={
                "class": "dropdown-menu"
            })
            for title, package, model in _contenttypes[page.content_model]:
                li = etree.SubElement(ul, "li")
                a = etree.SubElement(li, 'a', attrib={
                    'href': '/ga_resources/createpage/?module={module}&classname={classname}&parent={slug}'.format(
                        module=package,
                        classname=model,
                        slug=page.slug)
                })
                a.text = title
        else:
            return ""

        print etree.tostring(div, pretty_print=True)
        return etree.tostring(div, pretty_print=True)


@register.tag("subpage_button")
def do_add_subpage(parser, token):
    return SubpageNode()