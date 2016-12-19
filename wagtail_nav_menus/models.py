import json
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch
from django.utils.html import format_html_join
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from .loading import get_class
from .utils import date_handler
from .defaults import (
    WAGTAIL_NAV_MENU_TYPES_DEFAULT, WAGTAIL_NAV_MENU_CHOICES_DEFAULT)
from pprint import pprint

NAV_MENU_CHOICES = getattr(
    settings,
    'WAGTAIL_NAV_MENU_CHOICES',
    WAGTAIL_NAV_MENU_CHOICES_DEFAULT
)


class AbstractPageBlock(blocks.StructBlock):
    override_title = blocks.CharBlock(required=False)
    open_in_new_tab = blocks.BooleanBlock(required=False)

    class Meta:
        icon = 'link'
        template = 'nav_menus/menu_link.html'


class InternalPageBlock(AbstractPageBlock):
    page = blocks.PageChooserBlock()

    def get_serializable_data(self, obj):
        page = obj['page']
        result = obj
        result['page'] = page.serializable_data()
        result['page']['url'] = page.url
        return result


class ExternalPageBlock(AbstractPageBlock):
    link = blocks.URLBlock()


class DjangoURLBlock(AbstractPageBlock):
    """ A link that is generated from a Django reverse URL lookup
    """
    url_name = blocks.CharBlock()

    def get_serializable_data(self, obj):
        url_name = obj['url_name']
        result = obj
        try:
            result['url'] = reverse(url_name)
        except NoReverseMatch:
            result['url'] = "Not Found"
        return result


URL_REGEX = r'^(?!www\.|(?:http|ftp)s?://|[A-Za-z]:\\|//).*'


class RelativeURLBlock(AbstractPageBlock):
    link = blocks.RegexBlock(regex=URL_REGEX, error_mesage={
        'invalid': "Not a relative URL"
    })


NAV_MENU_TYPES = getattr(
    settings,
    'WAGTAIL_NAV_MENU_TYPES',
    WAGTAIL_NAV_MENU_TYPES_DEFAULT
)

nav_content = []
for name, module_label, class_name in NAV_MENU_TYPES:
    nav_content.append(
        (name, get_class(module_label, class_name)()),
    )

class HackedStreamBlock(blocks.StreamBlock):
#    def get_first_link(self, value, context=None):
#        return value[0].value['page'].url

    def render_basic(self, value, context=None):
        print(context)
        if value[0].value['override_title'] == 'Overview':
            return format_html_join(
                '\n', '<!--<div class="block-{1}">-->{0}<!--</div>-->',
                [
                    (child.render(context=context), child.block_type)
                    for child in value
                ]
            )
        else:
            return format_html_join(
                '\n', '<!--<div class="block-{1}">-->{0}<!--</div>-->',
                [
                    (child.render(context=context), child.block_type)
                    for child in value
                ]
            )

class NavCategoryBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    url = InternalPageBlock()
    sub_nav = HackedStreamBlock(nav_content)

    def get_url():
        return self.url.url

    def set_template(self, template):
        self.meta.template = template

    class Meta:
        icon = 'list-ul'


class NavMenu(models.Model):
    _nav_category_block = NavCategoryBlock()
    name = models.CharField(
        max_length=50,
        choices=NAV_MENU_CHOICES,
        unique=True)
    menu = StreamField([
        ('nav_category', _nav_category_block),
    ] + nav_content)

    panels = [
        FieldPanel('name'),
        StreamFieldPanel('menu'),
    ]

    def __str__(self):
        return self.name

    def stream_field_to_json(self, stream_field):
        """ Recursive function to turn the menu stream field into json """
        row = {}
        row['type'] = stream_field.block_type
        if hasattr(stream_field.block, 'get_serializable_data'):
            row['value'] = stream_field.block.get_serializable_data(
                stream_field.value)
        else:
            row['value'] = stream_field.value
        if row['type'] == "image" and row['value']:
            image = row['value']
            row['value'] = {
                "id": image.pk,
                "title": image.title,
                "url": image.file.url,
            }
        elif row['type'] == "nav_category":
            sub_nav = []
            for sub_stream_field in stream_field.value['sub_nav']:
                sub_nav.append(self.stream_field_to_json(sub_stream_field))
            row['value']['sub_nav'] = sub_nav
        return row

    def to_json(self):
        """ JSON representation of menu stream field """
        result = []
        for stream_field in self.menu:
            result.append(self.stream_field_to_json(stream_field))
        return json.dumps(result, default=date_handler)

    def set_category_template(self, category_template):
        self._nav_category_block.set_template(category_template)

    def set_link_template(self, link_template):
        for content_type in nav_content:
            if hasattr(content_type[1].meta, 'template'):
                content_type[1].meta.template = link_template
