from django.test import TestCase, override_settings, tag
from zero_settings import ZeroSettings


class TestZeroSettings(TestCase):
    def setUp(self):
        self.VALUE = "value"
        self.DEFAULTS = {
            "KEY": "key",
            "VALUE": "value",
            "LIST": [
                "list_1",
                "list_2",
            ],
            "TUPLE": (
                "tuple_1",
                "tuple_2",
            ),
            "DICT": {
                "1": 1,
                2: "2",
            },
            "IMPORT": "utils.TestClass",
            "IMPORT_LIST": [
                "utils.test_method_1",
                "utils.test_method_2",
            ],
        }
        self.IMPORT_STRINGS = [
            "IMPORT",
            "IMPORT_LIST",
        ]
        self.SETTINGS_DOC = "https://app.com/doc/settings"

        return super().setUp()

    @tag("args")
    def test_no_args(self):
        """
        Test no args
        """
        with self.assertRaises(TypeError):
            ZeroSettings()

    @tag("args")
    def test_basic_args(self):
        """
        Test basic args
        """
        ZeroSettings(
            key="APP",
            defaults={},
        )

    @tag("args", "key")
    def test_args_key(self):
        """
        Test wrong key values
        """
        for key in (["0"], ("0",), {"0": "0"}, None, 123, 123.4):
            with self.assertRaisesMessage(ValueError, "key must be string"):
                ZeroSettings(key=key, defaults={})

    @tag("args", "defaults")
    def test_args_defaults(self):
        """
        Test wrong defaults values
        """
        for defaults in (["0"], ("0",), None, "string", 123, 123.4):
            with self.assertRaisesMessage(ValueError, "defaults must be dict"):
                ZeroSettings(key="APP", defaults=defaults)

    @tag("args", "import_strings")
    def test_args_import_strings(self):
        """
        Test wrong import_strings values
        """
        for import_strings in ({"0": "0"}, "string", 123, 123.4):
            with self.assertRaisesMessage(ValueError, "import_strings must be list/tuple of strings or None"):
                ZeroSettings(key="APP", defaults={}, import_strings=import_strings)

    @tag("args", "removed_settings")
    def test_args_removed_settings(self):
        """
        Test wrong removed_settings values
        """
        for removed_settings in (["0"], ("0",), "string", 123, 123.4):
            with self.assertRaisesMessage(ValueError, "removed_settings must be dict of setting: msg or None"):
                ZeroSettings(key="APP", defaults={}, removed_settings=removed_settings)

    @tag("args", "settings_doc")
    def test_args_settings_doc(self):
        """
        Test wrong settings_doc values
        """
        for settings_doc in (["0"], ("0",), {1: 2}, 123, 123.4):
            with self.assertRaisesMessage(ValueError, "settings_doc must be string or None"):
                ZeroSettings(key="APP", defaults={}, settings_doc=settings_doc)

    @tag("args", "user_settings")
    def test_args_user_settings(self):
        """
        Test wrong user_settings values
        """
        for user_settings in (["0"], ("0",), "string", 123, 123.4):
            with self.assertRaisesMessage(ValueError, "user_settings must be dict or None"):
                ZeroSettings(key="APP", defaults={}, user_settings=user_settings)

    @tag("args", "use_cache")
    def test_args_use_cache(self):
        """
        Test wrong use_cache values
        """
        for use_cache in (["0"], ("0",), {1: 2}, "string", 123, 123.4):
            with self.assertRaisesMessage(ValueError, "use_cache must be boolean"):
                ZeroSettings(key="APP", defaults={}, use_cache=use_cache)

    @tag("args", "strict_defaults")
    def test_args_strict_defaults(self):
        """
        Test wrong strict_defaults values
        """
        for strict_defaults in (["0"], ("0",), {1: 2}, "string", 123, 123.4):
            with self.assertRaisesMessage(ValueError, "strict_defaults must be boolean"):
                ZeroSettings(key="APP", defaults={}, strict_defaults=strict_defaults)

    @tag("args", "pre_check_defaults")
    def test_args_pre_check_defaults(self):
        """
        Test wrong pre_check_defaults values
        """
        for pre_check_defaults in (["0"], ("0",), {1: 2}, "string", 123, 123.4):
            with self.assertRaisesMessage(ValueError, "pre_check_defaults must be boolean"):
                ZeroSettings(key="APP", defaults={}, pre_check_defaults=pre_check_defaults)

    @tag("args", "pre_check_imports")
    def test_args_pre_check_imports(self):
        """
        Test wrong pre_check_imports values
        """
        for pre_check_imports in (["0"], ("0",), {1: 2}, "string", 123, 123.4):
            with self.assertRaisesMessage(ValueError, "pre_check_imports must be boolean"):
                ZeroSettings(key="APP", defaults={}, pre_check_imports=pre_check_imports)

    @tag("args", "pre_check_removed")
    def test_args_pre_check_removed(self):
        """
        Test wrong pre_check_removed values
        """
        for pre_check_removed in (["0"], ("0",), {1: 2}, "string", 123, 123.4):
            with self.assertRaisesMessage(ValueError, "pre_check_removed must be boolean"):
                ZeroSettings(key="APP", defaults={}, pre_check_removed=pre_check_removed)

    @tag(
        "props",
        "has_default",
        "is_import",
        "is_removed",
    )
    def test_props(self):
        """
        Test basic props, _has_default, _is_import and _is_removed
        """
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            import_strings=self.IMPORT_STRINGS,
            removed_settings={"REMOVED": "removed"},
        )
        self.assertEqual(app_settings._has_default("KEY"), True)
        self.assertEqual(app_settings._has_default("NO_KEY"), False)
        self.assertEqual(app_settings._is_import("IMPORT"), True)
        self.assertEqual(app_settings._is_import("NO_IMPORT"), False)
        self.assertEqual(app_settings._is_removed("REMOVED"), True)
        self.assertEqual(app_settings._is_removed("NOT_REMOVED"), False)

    @tag(
        "attrs",
        "defaults",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_settings(self):
        """
        Test get different key values
        """
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS)
        self.assertEqual(app_settings.KEY, self.DEFAULTS["KEY"])
        self.assertEqual(app_settings.VALUE, self.DEFAULTS["VALUE"])
        self.assertEqual(app_settings.LIST, self.DEFAULTS["LIST"])
        self.assertEqual(app_settings.TUPLE, self.DEFAULTS["TUPLE"])
        self.assertEqual(app_settings.DICT, self.DEFAULTS["DICT"])
        self.assertEqual(app_settings.IMPORT, self.DEFAULTS["IMPORT"])
        self.assertEqual(app_settings.IMPORT_LIST, self.DEFAULTS["IMPORT_LIST"])

    @tag(
        "attrs",
        "defaults",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_settings_no_cache(self):
        """
        Test get different key values without cache
        """
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS, use_cache=False)
        self.assertEqual(app_settings.KEY, self.DEFAULTS["KEY"])
        self.assertEqual(app_settings.VALUE, self.DEFAULTS["VALUE"])
        self.assertEqual(app_settings.LIST, self.DEFAULTS["LIST"])
        self.assertEqual(app_settings.TUPLE, self.DEFAULTS["TUPLE"])
        self.assertEqual(app_settings.DICT, self.DEFAULTS["DICT"])
        self.assertEqual(app_settings.IMPORT, self.DEFAULTS["IMPORT"])
        self.assertEqual(app_settings.IMPORT_LIST, self.DEFAULTS["IMPORT_LIST"])

    @tag(
        "attrs",
        "defaults",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_settings_not_exists(self):
        """
        Test get a key that not exists
        """
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS)
        with self.assertRaisesMessage(AttributeError, "Invalid setting: 'APP.NO_KEY'"):
            app_settings.NO_KEY

    @tag(
        "attrs",
        "defaults",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_settings_not_exists_no_cache(self):
        """
        Test get a key that not exists without cache
        """
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS, use_cache=False)
        with self.assertRaisesMessage(AttributeError, "Invalid setting: 'APP.NO_KEY'"):
            app_settings.NO_KEY

    @tag(
        "attrs",
        "defaults",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"NOT_DEFAULT": "not_default"})
    def test_settings_not_default_exists_with_strict_defaults_pre_checked(self):
        """
        Test global user settings without default key
        """
        with self.assertRaisesMessage(AttributeError, "Invalid setting: 'APP.NOT_DEFAULT'"):
            ZeroSettings(
                key="APP",
                defaults=self.DEFAULTS,
                strict_defaults=True,
                pre_check_defaults=True,
            )

    @tag(
        "attrs",
        "defaults",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"NOT_DEFAULT": "not_default"})
    def test_settings_not_default_exists_with_strict_defaults_pre_checked_no_cache(self):
        """
        Test get a key with global user settings and without default key and cache
        """
        with self.assertRaisesMessage(AttributeError, "Invalid setting: 'APP.NOT_DEFAULT'"):
            ZeroSettings(
                key="APP",
                defaults=self.DEFAULTS,
                strict_defaults=True,
                pre_check_defaults=True,
                use_cache=False,
            )

    @tag(
        "attrs",
        "defaults",
        "use_cache",
        "strict_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"NOT_DEFAULT": "not_default"})
    def test_settings_not_default_exists_with_strict_defaults_not_pre_checked(self):
        """
        Test get a key with global user settings and without default key and pre check defaults
        """
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            strict_defaults=True,
            pre_check_defaults=False,
        )
        with self.assertRaisesMessage(AttributeError, "Invalid setting: 'APP.NOT_DEFAULT'"):
            app_settings.NOT_DEFAULT

    @tag(
        "attrs",
        "defaults",
        "strict_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"NOT_DEFAULT": "not_default"})
    def test_settings_not_default_exists_with_strict_defaults_not_pre_checked_no_cache(self):
        """
        Test get a key with global user settings and without default key, pre check defaults and cache
        """
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            strict_defaults=True,
            pre_check_defaults=False,
            use_cache=False,
        )
        with self.assertRaisesMessage(AttributeError, "Invalid setting: 'APP.NOT_DEFAULT'"):
            app_settings.NOT_DEFAULT

    @tag(
        "attrs",
        "defaults",
        "use_cache",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"NOT_DEFAULT": "not_default"})
    def test_settings_not_default_exists_with_not_strict_defaults_pre_checked(self):
        """
        Test get a key with global user settings and without default key and strict defaults
        """
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            strict_defaults=False,
            pre_check_defaults=True,
        )
        self.assertEqual(app_settings.NOT_DEFAULT, "not_default")

    @tag(
        "attrs",
        "defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"NOT_DEFAULT": "not_default"})
    def test_settings_not_default_exists_with_not_strict_defaults_pre_checked_no_cache(self):
        """
        Test get a key with global user settings and without default key, strict defaults and cache
        """
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            strict_defaults=False,
            pre_check_defaults=True,
            use_cache=False,
        )
        self.assertEqual(app_settings.NOT_DEFAULT, "not_default")

    @tag(
        "attrs",
        "defaults",
        "use_cache",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"NOT_DEFAULT": "not_default"})
    def test_settings_not_default_exists_with_not_strict_defaults_not_pre_checked(self):
        """
        Test get a key with global user settings and without default key, strict defaults and pre check defaults
        """
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            strict_defaults=False,
            pre_check_defaults=False,
        )
        self.assertEqual(app_settings.NOT_DEFAULT, "not_default")

    @tag(
        "attrs",
        "defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"NOT_DEFAULT": "not_default"})
    def test_settings_not_default_exists_with_not_strict_defaults_not_pre_checked_no_cache(self):
        """
        Test get a key with global user settings and without default key, strict defaults, pre check defaults and cache
        """
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            strict_defaults=False,
            pre_check_defaults=False,
            use_cache=False,
        )
        self.assertEqual(app_settings.NOT_DEFAULT, "not_default")

    @tag(
        "attrs",
        "user_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"KEY": "new_key"})
    def test_settings_with_global_user_settings(self):
        """
        Test get an override key with global user settings
        """
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS)
        self.assertNotEqual(app_settings.KEY, self.DEFAULTS["KEY"])
        self.assertEqual(app_settings.KEY, "new_key")

    @tag(
        "attrs",
        "user_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_settings_with_local_user_settings_not_defaults(self):
        """
        Test get a key with local user settings and without default key
        """
        user_settings = {"NOT_DEFAULT": "not_default"}
        with self.assertRaisesMessage(AttributeError, "Invalid setting: 'APP.NOT_DEFAULT'"):
            ZeroSettings(key="APP", defaults=self.DEFAULTS, user_settings=user_settings)

    @tag(
        "attrs",
        "user_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_settings_with_local_user_settings_not_defaults_no_pre_checked(self):
        """
        Test get a key with local user settings and without default key and pre check defaults
        """
        user_settings = {"NOT_DEFAULT": "not_default"}
        app_settings = ZeroSettings(
            key="APP", defaults=self.DEFAULTS, user_settings=user_settings, pre_check_defaults=False
        )
        with self.assertRaisesMessage(AttributeError, "Invalid setting: 'APP.NOT_DEFAULT'"):
            app_settings.NOT_DEFAULT

    @tag(
        "attrs",
        "user_settings",
        "use_cache",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_settings_with_local_user_settings_not_defaults_no_strict(self):
        """
        Test get a key with local user settings and without default key and strict defaults
        """
        user_settings = {"NOT_DEFAULT": "not_default"}
        app_settings = ZeroSettings(
            key="APP", defaults=self.DEFAULTS, user_settings=user_settings, strict_defaults=False
        )
        self.assertEqual(app_settings.NOT_DEFAULT, "not_default")

    @tag(
        "attrs",
        "user_settings",
        "use_cache",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_settings_with_local_user_settings_not_defaults_no_pre_checked_no_strict(self):
        """
        Test get a key with local user settings and without default key, strict defaults and pre check defaults
        """
        user_settings = {"NOT_DEFAULT": "not_default"}
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            user_settings=user_settings,
            pre_check_defaults=False,
            strict_defaults=False,
        )
        self.assertEqual(app_settings.NOT_DEFAULT, "not_default")

    @tag(
        "attrs",
        "user_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_settings_with_local_user_settings(self):
        """
        Test get an override key with local user settings
        """
        user_settings = {"VALUE": "new_value"}
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS, user_settings=user_settings)
        self.assertNotEqual(app_settings.VALUE, self.DEFAULTS["VALUE"])
        self.assertEqual(app_settings.VALUE, "new_value")

    @tag(
        "attrs",
        "user_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"VALUE": "value_1"})
    def test_settings_with_override_user_settings(self):
        """
        Test get an override key which local user settings override global user settings
        """
        user_settings = {"VALUE": "value_2"}
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS, user_settings=user_settings)
        self.assertNotEqual(app_settings.VALUE, self.DEFAULTS["VALUE"])
        self.assertEqual(app_settings.VALUE, "value_2")

    @tag(
        "attrs",
        "import_strings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_import_strings(self):
        """
        Test call import keys
        """
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS, import_strings=self.IMPORT_STRINGS)
        self.assertIsInstance(app_settings.IMPORT, type)
        self.assertEqual(app_settings.IMPORT.test_method_0(), "test_method_0")
        self.assertEqual(app_settings.IMPORT_LIST[0](), "test_method_1")
        self.assertEqual(app_settings.IMPORT_LIST[1](), "test_method_2")

    @tag(
        "attrs",
        "import_strings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"IMPORT": "utils.NotExists"})
    def test_import_strings_not_exists_pre_checked(self):
        """
        Test pre check wrong import string
        """
        with self.assertRaises(ImportError):
            ZeroSettings(key="APP", defaults=self.DEFAULTS, import_strings=self.IMPORT_STRINGS)

    @tag(
        "attrs",
        "import_strings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_removed",
    )
    @override_settings(APP={"IMPORT": "utils.NotExists"})
    def test_import_strings_not_exists_no_pre_checked(self):
        """
        Test check wrong import string
        """
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            import_strings=self.IMPORT_STRINGS,
            pre_check_imports=False,
        )
        with self.assertRaises(ImportError):
            app_settings.IMPORT

    @tag(
        "attrs",
        "import_strings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"IMPORT_LIST": ["utils.NotExists"]})
    def test_import_strings_not_exists_list(self):
        """
        Test pre check wrong import string list
        """
        with self.assertRaises(ImportError):
            ZeroSettings(key="APP", defaults=self.DEFAULTS, import_strings=self.IMPORT_STRINGS)

    @tag(
        "attrs",
        "import_strings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_removed",
    )
    @override_settings(APP={"IMPORT_LIST": ["utils.NotExists"]})
    def test_import_strings_not_exists_list_no_pre_checked(self):
        """
        Test check wrong import string list
        """
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            import_strings=self.IMPORT_STRINGS,
            pre_check_imports=False,
        )
        with self.assertRaises(ImportError):
            app_settings.IMPORT_LIST[0]

    @tag(
        "attrs",
        "import_strings",
        "user_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_import_strings_not_exists_with_local_user_settings(self):
        """
        Test pre check wrong import string with local user settings
        """
        user_settings = {"IMPORT": "utils.NotExists"}
        with self.assertRaises(ImportError):
            ZeroSettings(
                key="APP",
                defaults=self.DEFAULTS,
                import_strings=self.IMPORT_STRINGS,
                user_settings=user_settings,
            )

    @tag(
        "attrs",
        "import_strings",
        "user_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_removed",
    )
    def test_import_strings_not_exists_with_local_user_settings_no_pre_checked(self):
        """
        Test check wrong import string with local user settings
        """
        user_settings = {"IMPORT": "utils.NotExists"}
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            import_strings=self.IMPORT_STRINGS,
            user_settings=user_settings,
            pre_check_imports=False,
        )
        with self.assertRaises(ImportError):
            app_settings.IMPORT

    @tag(
        "attrs",
        "import_strings",
        "user_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_import_strings_not_exists_list_with_local_user_settings(self):
        """
        Test pre check wrong import string list with local user settings
        """
        user_settings = {"IMPORT_LIST": ["utils.NotExists"]}
        with self.assertRaises(ImportError):
            ZeroSettings(
                key="APP",
                defaults=self.DEFAULTS,
                import_strings=self.IMPORT_STRINGS,
                user_settings=user_settings,
            )

    @tag(
        "attrs",
        "import_strings",
        "user_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_removed",
    )
    def test_import_strings_not_exists_list_with_local_user_settings(self):
        """
        Test check wrong import string list with local user settings
        """
        user_settings = {"IMPORT_LIST": ["utils.NotExists"]}
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            import_strings=self.IMPORT_STRINGS,
            user_settings=user_settings,
            pre_check_imports=False,
        )
        with self.assertRaises(ImportError):
            app_settings.IMPORT_LIST[0]

    @tag(
        "attrs",
        "removed_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"REMOVED": "value"})
    def test_removed_settings(self):
        """
        Test pre check removed settings with global user settings
        """
        with self.assertRaisesMessage(RuntimeError, "The 'APP.REMOVED' setting has been removed."):
            ZeroSettings(
                key="APP",
                defaults=self.DEFAULTS,
                removed_settings={
                    "REMOVED": None,
                },
            )

    @tag(
        "attrs",
        "removed_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_imports",
    )
    @override_settings(APP={"REMOVED": "value"})
    def test_removed_settings_no_pre_checked(self):
        """
        Test check removed settings with global user settings and without pre checked defaults and removed
        """
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            removed_settings={
                "REMOVED": None,
            },
            pre_check_defaults=False,
            pre_check_removed=False,
        )
        with self.assertRaisesMessage(RuntimeError, "The 'APP.REMOVED' setting has been removed."):
            app_settings.REMOVED

    @tag("attrs", "removed_settings")
    @override_settings(APP={"REMOVED": "value"})
    def test_removed_settings_with_message(self):
        """
        Test pre check removed settings with global user settings and custom message
        """
        with self.assertRaisesMessage(RuntimeError, "removed"):
            ZeroSettings(
                key="APP",
                defaults=self.DEFAULTS,
                removed_settings={"REMOVED": "removed"},
            )

    @tag(
        "attrs",
        "removed_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_imports",
    )
    @override_settings(APP={"REMOVED": "value"})
    def test_removed_settings_with_message_no_pre_checked(self):
        """
        Test check removed settings with global user settings and custom message without pre check defaults and removed
        """
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            removed_settings={"REMOVED": "removed"},
            pre_check_defaults=False,
            pre_check_removed=False,
        )
        with self.assertRaisesMessage(RuntimeError, "removed"):
            app_settings.REMOVED

    @tag(
        "attrs",
        "removed_settings",
        "settings_doc",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    @override_settings(APP={"REMOVED": "value"})
    def test_removed_settings_with_settings_doc(self):
        """
        Test pre check removed settings with global user settings and settings doc
        """
        with self.assertRaisesMessage(
            RuntimeError,
            "The 'APP.REMOVED' setting has been removed. Please refer to '%s' for available settings."
            % (self.SETTINGS_DOC),
        ):
            ZeroSettings(
                key="APP",
                defaults=self.DEFAULTS,
                removed_settings={"REMOVED": None},
                settings_doc=self.SETTINGS_DOC,
            )

    @tag(
        "attrs",
        "removed_settings",
        "settings_doc",
        "use_cache",
        "strict_defaults",
        "pre_check_imports",
    )
    @override_settings(APP={"REMOVED": "value"})
    def test_removed_settings_with_settings_doc_no_pre_checked(self):
        """
        Test check removed settings with global user settings and settings doc
        """
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            removed_settings={"REMOVED": None},
            settings_doc=self.SETTINGS_DOC,
            pre_check_defaults=False,
            pre_check_removed=False,
        )
        with self.assertRaisesMessage(
            RuntimeError,
            "The 'APP.REMOVED' setting has been removed. Please refer to '%s' for available settings."
            % (self.SETTINGS_DOC),
        ):
            app_settings.REMOVED

    @tag(
        "attrs",
        "removed_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_removed_settings_with_local_user_settings(self):
        """
        Test pre check removed settings with local user settings
        """
        user_settings = {"REMOVED": "value"}
        with self.assertRaisesMessage(RuntimeError, "The 'APP.REMOVED' setting has been removed."):
            ZeroSettings(
                key="APP",
                defaults=self.DEFAULTS,
                removed_settings={"REMOVED": None},
                user_settings=user_settings,
            )

    @tag(
        "attrs",
        "removed_settings",
        "use_cache",
        "strict_defaults",
        "pre_check_imports",
    )
    def test_removed_settings_with_local_user_settings_no_pre_checked(self):
        """
        Test check removed settings with local user settings and without pre check defaults and removed
        """
        user_settings = {"REMOVED": "value"}
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            removed_settings={"REMOVED": None},
            user_settings=user_settings,
            pre_check_defaults=False,
            pre_check_removed=False,
        )
        with self.assertRaisesMessage(RuntimeError, "The 'APP.REMOVED' setting has been removed."):
            app_settings.REMOVED

    @tag(
        "attrs",
        "removed_settings",
        "settings_doc",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_removed_settings_with_settings_doc_and_local_user_settings(self):
        """
        Test pre check removed settings with local user settings and settings doc
        """
        user_settings = {"REMOVED": "value"}
        with self.assertRaisesMessage(
            RuntimeError,
            "The 'APP.REMOVED' setting has been removed. Please refer to '%s' for available settings."
            % (self.SETTINGS_DOC),
        ):
            ZeroSettings(
                key="APP",
                defaults=self.DEFAULTS,
                removed_settings={
                    "REMOVED": None,
                },
                user_settings=user_settings,
                settings_doc=self.SETTINGS_DOC,
            )

    @tag(
        "attrs",
        "removed_settings",
        "settings_doc",
        "use_cache",
        "strict_defaults",
        "pre_check_imports",
    )
    def test_removed_settings_with_settings_doc_and_local_user_settings_no_pre_checked(self):
        """
        Test check removed settings with local user settings and settings doc and without pre check defaults and removed
        """
        user_settings = {"REMOVED": "value"}
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            removed_settings={
                "REMOVED": None,
            },
            user_settings=user_settings,
            settings_doc=self.SETTINGS_DOC,
            pre_check_defaults=False,
            pre_check_removed=False,
        )
        with self.assertRaisesMessage(
            RuntimeError,
            "The 'APP.REMOVED' setting has been removed. Please refer to '%s' for available settings."
            % (self.SETTINGS_DOC),
        ):
            app_settings.REMOVED

    @tag(
        "attrs",
        "cache",
        "override",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_overrides_before_being_cached(self):
        """
        Test override settings before being cached
        """
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS)
        with self.settings(APP={"VALUE": "new_value"}):
            self.assertEqual(app_settings.VALUE, "new_value")

    @tag(
        "attrs",
        "cache",
        "override",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_overrides_being_cached(self):
        """
        Test override settings being cached
        """
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS)
        app_settings.VALUE
        with self.settings(APP={"VALUE": "new_value"}):
            self.assertEqual(app_settings.VALUE, "value")
            self.assertNotEqual(app_settings.VALUE, "new_value")

    @tag(
        "attrs",
        "cache",
        "override",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_overrides_with_no_cache(self):
        """
        Test override settings with no cache
        """
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS, use_cache=False)
        app_settings.VALUE
        with self.settings(APP={"VALUE": "new_value"}):
            self.assertEqual(app_settings.VALUE, "new_value")

    @tag(
        "attrs",
        "cache",
        "override",
        "use_cache",
        "strict_defaults",
        "pre_check_defaults",
        "pre_check_imports",
        "pre_check_removed",
    )
    def test_overrides_and_use_clear_cache(self):
        """
        Test override settings and user clear cache
        """
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS)
        app_settings.VALUE
        with self.settings(APP={"VALUE": "new_value"}):
            app_settings._clear_cache()
            self.assertEqual(app_settings.VALUE, "new_value")
