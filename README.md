# Wagtail Nav Menus

Wagtail Nav Menus is a app to provide highly customizable menus in wagtail by leveraging StreamFields.

# Why

Remember when websites had tree structures with logical menus that followed the same structure?
For many those days are gone. We are asked to create arbitrary menu items, place value props
in menus that aren't even links, and build highly interactive menus with javascript.

Wagtail Nav Menus addresses this by using stream fields to support arbitrary items in the menu and
gives you options to render the menus as both django templates or json for your js tooling to consume.

![demo](demo.png)

## Built in Components

- Nav Category - a grouping of other components - for things like sub navigation
- Page Link - Link to a wagtail Page
- External Link - Django URLField link
- Django Link - Reverse django view lookups
- Relative URL - Regex enforced relative links
- Image
- Html

# Install

1. Install `wagtail-nav-menus` with pip
2. Add `wagtail_nav_menus` to INSTALLED_APPS
3. Ensure that `wagtail.contrib.modeladmin` is included in INSTALLED_APPS

## Settings

You can add other streamfields like this:

```
from wagtail_nav_menus.defaults import WAGTAIL_NAV_MENU_TYPES_DEFAULT

WAGTAIL_NAV_MENU_TYPES = NAV_MENU_TYPES_DEFAULT + [
    ('page_link_with_image', 'nav_menus_ext.models', 'InternalPageImageBlock'),
    ('page_link_with_image', 'nav_menus_ext.models', 'NavAdvertBlock'),
]
```

The schema here is ('name', 'module_path', 'class name')

Edit menu name choices. The default is top and footer. These represent different menus for your webpage.
The names are arbitrary - but you will look them up by name in templates.

```
WAGTAIL_NAV_MENU_CHOICES_DEFAULT = (
    ("top", "Top"),
    ("footer", "Footer"),
)
```

## Usage

Nav Menus should appear in wagtail's settings sidebar tab. CMS uses can control them here.

You may use some template tags to use these in your site.

### get_nav_menu

Use this to insert the menu using django templates.

``` 
{% load nav_menu_tags %}
{% get_nav_menu 'footer' %}
```

Use the optional template argument to specify a custom template.

```
{% get_nav_menu 'footer' template='nav_menus/mobile_sidebar.html' %}
```

See the [templates folder](wagtail_nav_menus/templates/) in this repo for examples of rendering the menu.
You will want to copy these into your project's template folder to extend them.


### get_nav_menu_json

Use this to get the menu as a json object.

``` 
{% load nav_menu_tags %}
{% get_nav_menu_json 'top' as top %}
<div data-menu='{{ top }}'></div>
```
