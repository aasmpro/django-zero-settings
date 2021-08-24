from django.conf import settings as django_settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string


class ZeroSettings:
    """
    A settings object that allows your settings to be accessed as properties.
    Example:

        from zero_settings import ZeroSettings

        app_settings = ZeroSettings(
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
            import_strings=["TEST_IMPORT", "TEST_IMPORT_LIST"],

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

        print(app_settings.TEST_KEY)

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
        use_cache=True,
        strict_defaults=True,
        pre_check_defaults=True,
        pre_check_imports=True,
        pre_check_removed=True,
    ):
        if isinstance(key, str):
            self.__key = key
        else:
            raise ValueError("key must be string")

        if isinstance(defaults, dict):
            self.__defaults = defaults
        else:
            raise ValueError("defaults must be dict")

        if not import_strings:
            self.__import_strings = []
        elif isinstance(import_strings, (list, tuple)):
            self.__import_strings = import_strings
        else:
            raise ValueError("import_strings must be list/tuple of strings or None")

        if not removed_settings:
            self.__removed_settings = {}
        elif isinstance(removed_settings, dict):
            self.__removed_settings = removed_settings
        else:
            raise ValueError("removed_settings must be dict of setting: msg or None")

        if not settings_doc:
            self.__settings_doc = ""
        elif isinstance(settings_doc, str):
            self.__settings_doc = settings_doc
        else:
            raise ValueError("settings_doc must be string or None")

        if not user_settings:
            self.__user_settings = {}
        elif isinstance(user_settings, dict):
            self.__user_settings = user_settings
        else:
            raise ValueError("user_settings must be dict or None")

        if isinstance(use_cache, bool):
            self.__use_cache = use_cache
        else:
            raise ValueError("use_cache must be boolean")

        if isinstance(strict_defaults, bool):
            self.__strict_defaults = strict_defaults
        else:
            raise ValueError("strict_defaults must be boolean")

        if isinstance(pre_check_defaults, bool):
            self.__pre_check_defaults = pre_check_defaults
            if self.__pre_check_defaults and self.__strict_defaults:
                self.__check_defaults(self.__get_user_settings())
        else:
            raise ValueError("pre_check_defaults must be boolean")

        if isinstance(pre_check_imports, bool):
            self.__pre_check_imports = pre_check_imports
            if self.__pre_check_imports:
                self.__check_import_strings(self.__import_strings)
        else:
            raise ValueError("pre_check_imports must be boolean")

        if isinstance(pre_check_removed, bool):
            self.__pre_check_removed = pre_check_removed
            if self.__pre_check_removed:
                self.__check_removed_settings(self.__get_user_settings())
                self.__check_removed_settings(self.__defaults)
        else:
            raise ValueError("pre_check_removed must be boolean")

        self.__cached_attrs = set()

    def __has_default(self, attr):
        """
        True if attr is in defaults
        """
        return attr in self.__defaults

    def __is_removed(self, attr):
        """
        True if attr is in removed settings
        """
        return attr in self.__removed_settings

    def __is_import(self, attr):
        """
        True if attr is in import strings
        """
        return attr in self.__import_strings

    def __cache(self, attr, value):
        """
        Cache and set class attr if use_cache is True
        """
        if self.__use_cache:
            self.__cached_attrs.add(attr)
            setattr(self, attr, value)

    def __clear_cache(self, attr=None):
        """
        Remove cached attrs and settings
        """
        if not attr:
            for attr in self.__cached_attrs:
                delattr(self, attr)
            self.__cached_attrs.clear()
            if hasattr(self, "__cached_settings"):
                delattr(self, "__cached_settings")

        elif attr and hasattr(self, attr):
            delattr(self, attr)

    def __check_removed(self, attr):
        """
        Check if an attribute is removed from settings
        """
        if self.__is_removed(attr):
            msg = self.__removed_settings.get(attr, None)
            if not msg:
                msg = "The '%s.%s' setting has been removed." % (self.__key, attr)
                if self.__settings_doc:
                    msg += " Please refer to '%s' for available settings." % (self.__settings_doc)
            raise RuntimeError(msg)

    def __check_removed_settings(self, settings):
        """
        Check all setting keys for removed attributes
        """
        for attr in settings:
            self.__check_removed(attr)

    def __check_default_exists(self, attr):
        """
        Check if attribute exists in default settings
        """
        if not self.__has_default(attr):
            raise AttributeError("Invalid setting: '%s.%s'" % (self.__key, attr))

    def __check_defaults(self, settings):
        """
        Check all setting keys to exist in default settings
        """
        for attr in settings:
            self.__check_default_exists(attr)

    def __import_from_string(self, value, attr):
        """
        Attempt to import setting from a string representation.
        """
        try:
            return import_string(value)
        except ImportError as e:
            msg = "Could not import '%s' for setting '%s.%s'. %s: %s." % (
                value,
                self.__key,
                attr,
                e.__class__.__name__,
                e,
            )
            raise ImportError(msg)

    def __perform_import(self, value, attr):
        """
        If the given setting is a string import notation,
        then perform the necessary import or imports.
        """
        if value is None:
            return None
        elif isinstance(value, str):
            return self.__import_from_string(value, attr)
        elif isinstance(value, (list, tuple)):
            return [self.__import_from_string(item, attr) for item in value]
        return value

    def __import(self, attr):
        """
        Import and return imported value of attr or raise ImportError
        """
        value = self.__getattr(attr)
        return self.__perform_import(value, attr)

    def __check_import_strings(self, import_strings):
        """
        Check if all import strings are valid
        """
        for attr in import_strings:
            self.__import(attr)

    def __get_user_settings(self):
        """
        Get and update user settings with provided key
        """
        __cached_settings = getattr(django_settings, self.__key, {})
        if self.__user_settings:
            __cached_settings.update(self.__user_settings)

        return __cached_settings

    @property
    def __settings(self):
        """
        Return cached settings or create one
        """
        if self.__use_cache:
            if not hasattr(self, "__cached_settings"):
                self.__cached_settings = self.__get_user_settings()
            return self.__cached_settings
        else:
            return self.__get_user_settings()

    def __getattr(self, attr):
        """
        Return settings attr or raise error
        """
        try:
            return self.__settings[attr]
        except KeyError:
            return self.__defaults[attr]

    def __getattr__(self, attr):
        """
        Return settings attr and cache if use_cached is True
        """
        self.__check_removed(attr)
        if self.__strict_defaults:
            self.__check_default_exists(attr)

        value = self.__getattr(attr)

        if self.__is_import(attr):
            value = self.__perform_import(value, attr)

        self.__cache(attr, value)
        return value