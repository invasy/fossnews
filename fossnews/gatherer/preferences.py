from asgiref.sync import sync_to_async
from dynamic_preferences.exceptions import CachedValueNotFound
from dynamic_preferences.managers import PreferencesManager
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry as registry
from dynamic_preferences.settings import preferences_settings
from dynamic_preferences.types import FloatPreference, IntegerPreference, StringPreference

from .meta import bind_to


gatherer = Section('gatherer', verbose_name='Gatherer')


@registry.register
class UserAgent(StringPreference):
    section = gatherer
    name = 'user_agent'
    verbose_name = 'User agent'
    help_text = 'User agent for news gatherer.'
    default = 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'
    required = True


@registry.register
class ConnectionLimit(IntegerPreference):
    section = gatherer
    name = 'connection_limit'
    verbose_name = 'Connection limit'
    help_text = 'The total number of simultaneous connections.'
    default = 100


@registry.register
class ConnectionTimeout(FloatPreference):
    section = gatherer
    name = 'connection_timeout'
    verbose_name = 'Connection timeout'
    help_text = 'Total number of seconds for the whole request.'
    default = 10.


@registry.register
class ConnectionRetries(IntegerPreference):
    section = gatherer
    name = 'connection_retries'
    verbose_name = 'Connection retry attempts'
    help_text = 'Connection retry attempts.'
    default = 3


# Patch PreferencesManager to support async queries
@bind_to(PreferencesManager)
async def acreate_db_pref(self, section, name, value):
    kwargs = {
        "section": section,
        "name": name,
    }
    if self.instance:
        kwargs["instance"] = self.instance

    m = self.model(**kwargs)
    m.value = value
    raw_value = m.raw_value

    db_pref, created = await self.model.objects.aget_or_create(**kwargs)
    if created and db_pref.raw_value != raw_value:
        db_pref.raw_value = raw_value
        await sync_to_async(db_pref.save)()

    return db_pref


@bind_to(PreferencesManager)
async def aget_db_pref(self, section, name):
    try:
        pref = await self.queryset.aget(section=section, name=name)
    except self.model.DoesNotExist:
        pref_obj = self.pref_obj(section=section, name=name)
        pref = await self.acreate_db_pref(section=section, name=name, value=pref_obj.get('default'))

    return pref


@bind_to(PreferencesManager)
async def aget(self, key, no_cache=False):
    section, name = self.parse_lookup(key)
    if no_cache or not preferences_settings.ENABLE_CACHE:
        return await self.aget_db_pref(section=section, name=name).value

    try:
        return self.from_cache(section, name)
    except CachedValueNotFound:
        pass

    db_pref = await self.aget_db_pref(section=section, name=name)
    self.to_cache(db_pref)
    return db_pref.value
