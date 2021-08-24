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

            # manually define or override user settings,
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
            settings_doc="https://app.com/doc/settings",

            # whether to use cache or not
            # must be boolean
            use_cache=True,

            # whether to be strict on defaults or not,
            # if true, only default keys are valid in user settings,
            # must be boolean
            strict_defaults=True,

            # whether to pre check defaults or not
            # must be boolean
            pre_check_defaults=True,

            # whether to pre check imports or not
            # must be boolean
            pre_check_imports=True,

            # whether to pre check removed or not
            # must be boolean
            pre_check_removed=True,
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
            self._key = key
        else:
            raise ValueError("key must be string")

        if isinstance(defaults, dict):
            self._defaults = defaults
        else:
            raise ValueError("defaults must be dict")

        if not import_strings:
            self._import_strings = []
        elif isinstance(import_strings, (list, tuple)):
            self._import_strings = import_strings
        else:
            raise ValueError("import_strings must be list/tuple of strings or None")

        if not removed_settings:
            self._removed_settings = {}
        elif isinstance(removed_settings, dict):
            self._removed_settings = removed_settings
        else:
            raise ValueError("removed_settings must be dict of setting: msg or None")

        if not settings_doc:
            self._settings_doc = ""
        elif isinstance(settings_doc, str):
            self._settings_doc = settings_doc
        else:
            raise ValueError("settings_doc must be string or None")

        if not user_settings:
            self._user_settings = {}
        elif isinstance(user_settings, dict):
            self._user_settings = user_settings
        else:
            raise ValueError("user_settings must be dict or None")

        if isinstance(use_cache, bool):
            self._use_cache = use_cache
        else:
            raise ValueError("use_cache must be boolean")

        if isinstance(strict_defaults, bool):
            self._strict_defaults = strict_defaults
        else:
            raise ValueError("strict_defaults must be boolean")

        if isinstance(pre_check_imports, bool):
            self._pre_check_imports = pre_check_imports
            if self._pre_check_imports:
                self._check_import_strings(self._import_strings)
        else:
            raise ValueError("pre_check_imports must be boolean")

        if isinstance(pre_check_removed, bool):
            self._pre_check_removed = pre_check_removed
            if self._pre_check_removed:
                self._check_removed_settings(self._get_user_settings())
                self._check_removed_settings(self._defaults)
        else:
            raise ValueError("pre_check_removed must be boolean")

        if isinstance(pre_check_defaults, bool):
            self._pre_check_defaults = pre_check_defaults
            if self._pre_check_defaults and self._strict_defaults:
                self._check_defaults(self._get_user_settings())
        else:
            raise ValueError("pre_check_defaults must be boolean")

        self._cached_attrs = set()

    def _has_default(self, attr):
        """
        True if attr is in defaults
        """
        return attr in self._defaults

    def _is_removed(self, attr):
        """
        True if attr is in removed settings
        """
        return attr in self._removed_settings

    def _is_import(self, attr):
        """
        True if attr is in import strings
        """
        return attr in self._import_strings

    def _cache(self, attr, value):
        """
        Cache and set class attr if use_cache is True
        """
        if self._use_cache:
            self._cached_attrs.add(attr)
            setattr(self, attr, value)

    def _clear_cache(self, attr=None):
        """
        Remove cached attrs and settings
        """
        if not attr:
            for attr in self._cached_attrs:
                delattr(self, attr)
            self._cached_attrs.clear()
            if hasattr(self, "_cached_settings"):
                delattr(self, "_cached_settings")

        elif attr and hasattr(self, attr):
            delattr(self, attr)

    def _check_removed(self, attr):
        """
        Check if an attribute is removed from settings
        """
        if self._is_removed(attr):
            msg = self._removed_settings.get(attr, None)
            if not msg:
                msg = "The '%s.%s' setting has been removed." % (self._key, attr)
                if self._settings_doc:
                    msg += " Please refer to '%s' for available settings." % (self._settings_doc)
            raise RuntimeError(msg)

    def _check_removed_settings(self, settings):
        """
        Check all setting keys for removed attributes
        """
        for attr in settings:
            self._check_removed(attr)

    def _check_default_exists(self, attr):
        """
        Check if attribute exists in default settings
        """
        if self._strict_defaults:
            if not self._has_default(attr):
                raise AttributeError("Invalid setting: '%s.%s'" % (self._key, attr))

    def _check_defaults(self, settings):
        """
        Check all setting keys to exist in default settings
        """
        if self._strict_defaults:
            for attr in settings:
                self._check_default_exists(attr)

    def _import_from_string(self, value, attr):
        """
        Attempt to import setting from a string representation.
        """
        try:
            return import_string(value)
        except ImportError as e:
            msg = "Could not import '%s' for setting '%s.%s'. %s." % (
                value,
                self._key,
                attr,
                e,
            )
            raise ImportError(msg)

    def _perform_import(self, value, attr):
        """
        If the given setting is a string import notation,
        then perform the necessary import or imports.
        """
        if value is None:
            return None
        elif isinstance(value, str):
            return self._import_from_string(value, attr)
        elif isinstance(value, (list, tuple)):
            return [self._import_from_string(item, attr) for item in value]
        return value

    def _import(self, attr):
        """
        Import and return imported value of attr or raise ImportError
        """
        value = self._getattr(attr)
        return self._perform_import(value, attr)

    def _check_import_strings(self, import_strings):
        """
        Check if all import strings are valid
        """
        for attr in import_strings:
            self._import(attr)

    def _get_user_settings(self):
        """
        Get and update user settings with provided key
        """
        _cached_settings = getattr(django_settings, self._key, {})
        if self._user_settings:
            _cached_settings.update(self._user_settings)

        return _cached_settings

    @property
    def _settings(self):
        """
        Return cached settings or create one
        """
        if self._use_cache:
            if not hasattr(self, "_cached_settings"):
                self._cached_settings = self._get_user_settings()
            return self._cached_settings
        else:
            return self._get_user_settings()

    def _getattr(self, attr):
        """
        Return settings attr or raise error
        """
        try:
            try:
                return self._settings[attr]
            except KeyError:
                return self._defaults[attr]
        except:
            raise AttributeError("Invalid setting: '%s.%s'" % (self._key, attr))

    def __getattr__(self, attr):
        """
        Return settings attr and cache if use_cached is True
        """
        self._check_removed(attr)
        self._check_default_exists(attr)

        value = self._getattr(attr)

        if self._is_import(attr):
            value = self._perform_import(value, attr)

        self._cache(attr, value)
        return value
