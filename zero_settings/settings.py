from django.conf import settings as django_settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string


class ZeroSettings:
    """
    A settings object that allows your settings to be accessed as properties.
    Example:

        from zero_settings import ZeroSettings

        settings = ZeroSettings(
            # key will be used to get user settings from Django settings
            # required, must be string
            key="ZERO_SETTINGS",

            # defaults settings
            # required, must be dict
            defaults={
                "TEST_KEY": "test_key"
                "TEST_IMPORT": "module.file.class_name",
                "TEST_IMPORT_LIST": [
                    "module.file.class_name_1",
                    "module.file.class_name_2",
                ]
            },

            # manually defining user settings,
            # by default settings will be loaded from Django settings with key,
            # optional, can be dict or None
            user_settings=None,

            # list of settings that must be imported, lazy check,
            # optional, can be list/tuple or None
            import_settings=["TEST_IMPORT", "TEST_IMPORT_LIST"],

            # dict of settings that had be removed,
            # message can be None or empty string to show default,
            # optional, can be dict or None
            removed_settings={
                "TEST_REMOVED": "An error message to show",
                "TEST_ANOTHER_REMOVED": "", # or None
            },

            # settings documents location, to refer user to
            # optional, can be str or None
            settings_doc="https://app.com/doc/settings"
        )

        print(settings.TEST_KEY)

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(
        self,
        key,
        defaults,
        user_settings=None,
        import_strings=None,
        removed_settings=None,
        settings_doc=None,
    ):
        if isinstance(self.key, str):
            self.key = key
        else:
            raise ValueError("key must be a string")

        if isinstance(defaults, dict):
            self.defaults = defaults
        else:
            raise ValueError("defaults must be a dict")

        if not import_strings:
            self.import_strings = []
        elif isinstance(import_strings, (list, tuple)):
            self.import_strings = import_strings
        else:
            raise ValueError("import_strings must be a list/tuple of strings or None")

        if not removed_settings:
            self.removed_settings = {}
        elif isinstance(removed_settings, dict):
            self.removed_settings = removed_settings
        else:
            raise ValueError("removed_settings must be a dict of setting: msg or None")

        if not settings_doc:
            self.settings_doc = ""
        if isinstance(settings_doc, str):
            self.settings_doc = settings_doc
        else:
            raise ValueError("settings_doc must be a string or None")

        self._user_settings = self.__check_user_settings(user_settings)
        self._cached_attrs = set()

    def __check_user_settings(self, user_settings):
        """
        Check settings for removed keys
        """
        if not user_settings:
            return {}
        if isinstance(user_settings, dict):
            if self.removed_settings:
                for setting in self.removed_settings:
                    if setting in user_settings:
                        msg = user_settings.get(setting, None)
                        if not msg:
                            msg = "The '%s.%s' setting has been removed." % (self.key, setting)
                            if self.settings_doc:
                                msg += " Please refer to '%s' for available settings." % (self.settings_doc)
                        raise RuntimeError(msg)
            return user_settings
        else:
            raise ValueError("user_settings must be a dict or None")

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            _user_settings = getattr(django_settings, self.key, {})
            self._user_settings = self.__check_user_settings(_user_settings)
        return self._user_settings

    def import_from_string(self, val, setting_name):
        """
        Attempt to import a class from a string representation.
        """
        try:
            return import_string(val)
        except ImportError as e:
            msg = "Could not import '%s.%s' for setting '%s'. %s: %s." % (
                self.key,
                val,
                setting_name,
                e.__class__.__name__,
                e,
            )
            raise ImportError(msg)

    def perform_import(self, val, setting_name):
        """
        If the given setting is a string import notation,
        then perform the necessary import or imports.
        """
        if val is None:
            return None
        elif isinstance(val, str):
            return self.import_from_string(val, setting_name)
        elif isinstance(val, (list, tuple)):
            return [self.import_from_string(item, setting_name) for item in val]
        return val

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid setting: '%s.%s'" % (self.key, attr))

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = self.perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self):
        """
        Remove _cached_attrs and _user_settings
        """
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


def register_reload(settings):
    """
    Register your settings to auto reload on settings change.
    Example:

        from zero_settings import ZeroSettings, register_reload

        # create your app settings
        app_settings = ZeroSettings(...)

        # register app settings
        register_reload(app_settings)
    """

    def reload_settings(*args, **kwargs):
        setting = kwargs["setting"]
        if setting == settings.key:
            settings.reload()

    setting_changed.connect(reload_settings)