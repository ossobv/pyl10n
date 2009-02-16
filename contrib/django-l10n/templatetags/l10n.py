from django import template
import pyl10n as locale
# Or alternately, if you've installed pyl10n in the django l10n dir:
#import l10n.pyl10n as locale, l10n.pyl10n.pyl10n_core as locale_config, os
#locale_config._locale_path = os.path.join(os.path.dirname(__file__), '..', '..', 'locale')


register = template.Library()


@register.filter
def lcmon(value):
    if value in (None, ''):
        return '-'
    return locale.currency(value, symbol=False, grouping=True)
lcmon.is_safe = True # no one uses < > & ' ", right?

@register.filter
def lcnum(value, formatstr='%.12g'):
    if value in (None, ''):
        return '-'
    return locale.format(formatstr, float(value), grouping=True)
lcnum.is_safe = True # no one uses < > & ' ", right?

@register.filter
def lcdate(value):
    return locale.format_date(value)
lcdate.is_safe = True # no one uses < > & ' ", right?

@register.filter
def lcdatetime(value):
    return locale.format_datetime(value)
lcdatetime.is_safe = True # no one uses < > & ' ", right?

@register.filter
def lctime(value):
    return locale.format_time(value)
lctime.is_safe = True # no one uses < > & ' ", right?
