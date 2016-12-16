from django.template import Library, loader, Context
from ..models import NavMenu

register = Library()


@register.simple_tag(takes_context=True)
def get_nav_menu(context, menu_name, calling_page=None,
        menu_template='nav_menus/tags/menu.html',
        link_template='nav_menus/menu_link.html',
        category_template='nav_menus/nav_category.html'):
    nav_menu = NavMenu.objects.get_or_create(name=menu_name)[0]

    # Set templates from optional tag kwargs
    nav_menu.set_category_template(category_template)
    nav_menu.set_link_template(link_template)
    t = loader.get_template(menu_template)

    return t.render(Context({
        'calling_page': calling_page,
        'menu_items': nav_menu.menu,
        'request': context['request'],
    }))


@register.simple_tag
def get_nav_menu_json(menu_name):
    nav_menu = NavMenu.objects.get_or_create(name=menu_name)[0]
    return nav_menu.to_json()
