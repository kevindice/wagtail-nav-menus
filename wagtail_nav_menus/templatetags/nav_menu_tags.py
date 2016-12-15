from django.template import Library, loader, Context
from ..models import NavMenu

register = Library()


@register.simple_tag(takes_context=True)
def get_nav_menu(context, menu_name, calling_page=None, template='nav_menus/tags/menu.html'):
    nav_menu = NavMenu.objects.get_or_create(name=menu_name)[0]
    t = loader.get_template(template)
    return t.render(Context({
        'calling_page': calling_page,
        'menu_items': nav_menu.menu,
        'request': context['request'],
    }))


@register.simple_tag
def get_nav_menu_json(menu_name):
    nav_menu = NavMenu.objects.get_or_create(name=menu_name)[0]
    return nav_menu.to_json()
