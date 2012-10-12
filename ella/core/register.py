from django import forms
from django import template
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator

from app_data import app_registry, AppDataForm, AppDataContainer

from ella.core.models import Category, Listing
from ella.core.conf import core_settings
from ella.core.cache.redis import connect_signals


class CategoryAppForm(AppDataForm):
    archive_template = forms.CharField(initial=core_settings.ARCHIVE_TEMPLATE, required=False)
    no_home_listings = forms.BooleanField(initial=core_settings.CATEGORY_NO_HOME_LISTINGS, required=False)
    listing_handler = forms.CharField(initial='default', required=False)
    paginate_by = forms.IntegerField(label=_('Paginate by'),
        initial=core_settings.CATEGORY_LISTINGS_PAGINATE_BY, required=False,
        help_text=_('How many records to show on one listing page.'))
    propagate_listings = forms.BooleanField(label=_('Propagate listings'),
        initial=True, required=False, help_text=_('Should propagate listings '
        'from child categories?'))

class EllaAppDataContainer(AppDataContainer):
    form_class = CategoryAppForm

    def get_listings(self, **kwargs):
        return Listing.objects.get_queryset_wrapper(self._instance, **kwargs)

    def get_listings_page(self, page_no, paginate_by=None, **kwargs):
        paginate_by = paginate_by or self.paginate_by
        paginator = Paginator(self.get_listings(**kwargs), paginate_by)

        if page_no > paginator.num_pages or page_no < 1:
            raise Http404(_('Invalid page number %r') % page_no)

        return paginator.page(page_no)
app_registry.register('ella', EllaAppDataContainer, Category)


# connect redis listing handler signals
connect_signals()

# add some of our templatetags to builtins

# add core templatetags to builtin so that you don't have to invoke {% load core %} in every template
template.add_to_builtins('ella.core.templatetags.core')
# keep this here for backwards compatibility
template.add_to_builtins('ella.core.templatetags.related')
# and custom urls
template.add_to_builtins('ella.core.templatetags.custom_urls_tags')
# and the same for i18n
template.add_to_builtins('django.templatetags.i18n')
# and photos are always useful
template.add_to_builtins('ella.photos.templatetags.photos')

