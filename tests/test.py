from django.test import TestCase, override_settings
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
        self.IMPORT_SETRINGS = [
            "IMPORT",
            "IMPORT_LIST",
        ]
        self.SETTINGS_DOC = "https://app.com/doc/settings"
        return super().setUp()

    def test_no_args(self):
        with self.assertRaises(TypeError):
            ZeroSettings()

    def test_basic_args(self):
        ZeroSettings(key="APP", defaults={})

    def test_args_key(self):
        for key in (["0"], ("0",), {"0": "0"}, None, 123, 123.4):
            with self.assertRaisesMessage(ValueError, "key must be a string"):
                ZeroSettings(key=key, defaults={})

    def test_args_defaults(self):
        for defaults in (["0"], ("0",), None, "string", 123, 123.4):
            with self.assertRaisesMessage(ValueError, "defaults must be a dict"):
                ZeroSettings(key="APP", defaults=defaults)

    def test_args_import_strings(self):
        for import_strings in ({"0": "0"}, "string", 123, 123.4):
            with self.assertRaisesMessage(ValueError, "import_strings must be a list/tuple of strings or None"):
                ZeroSettings(key="APP", defaults={}, import_strings=import_strings)

    def test_args_removed_settings(self):
        for removed_settings in (["0"], ("0",), "string", 123, 123.4):
            with self.assertRaisesMessage(ValueError, "removed_settings must be a dict of setting: msg or None"):
                ZeroSettings(key="APP", defaults={}, removed_settings=removed_settings)

    def test_args_settings_doc(self):
        for settings_doc in (["0"], ("0",), {1: 2}, 123, 123.4):
            with self.assertRaisesMessage(ValueError, "settings_doc must be a string or None"):
                ZeroSettings(key="APP", defaults={}, settings_doc=settings_doc)

    def test_args_user_settings(self):
        for user_settings in (["0"], ("0",), "string", 123, 123.4):
            with self.assertRaisesMessage(ValueError, "user_settings must be a dict or None"):
                ZeroSettings(key="APP", defaults={}, user_settings=user_settings)

    def test_settings(self):
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS)
        self.assertEqual(app_settings.KEY, self.DEFAULTS["KEY"])
        self.assertEqual(app_settings.VALUE, self.DEFAULTS["VALUE"])
        self.assertEqual(app_settings.LIST, self.DEFAULTS["LIST"])
        self.assertEqual(app_settings.TUPLE, self.DEFAULTS["TUPLE"])
        self.assertEqual(app_settings.DICT, self.DEFAULTS["DICT"])
        self.assertEqual(app_settings.IMPORT, self.DEFAULTS["IMPORT"])
        self.assertEqual(app_settings.IMPORT_LIST, self.DEFAULTS["IMPORT_LIST"])

    def test_settings_not_exists(self):
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS)
        with self.assertRaisesMessage(AttributeError, "Invalid setting: 'APP.NO_KEY'"):
            app_settings.NO_KEY

    @override_settings(APP={"KEY": "new_key"})
    def test_settings_with_global_user_settings(self):
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS)
        self.assertNotEqual(app_settings.KEY, self.DEFAULTS["KEY"])
        self.assertEqual(app_settings.KEY, "new_key")

    def test_settings_with_local_user_settings(self):
        user_settings = {"VALUE": "new_value"}
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS, user_settings=user_settings)
        self.assertNotEqual(app_settings.VALUE, self.DEFAULTS["VALUE"])
        self.assertEqual(app_settings.VALUE, "new_value")

    def test_import_strings(self):
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS, import_strings=self.IMPORT_SETRINGS)
        self.assertIsInstance(app_settings.IMPORT, type)
        self.assertEqual(app_settings.IMPORT.test_method_0(), "test_method_0")
        self.assertEqual(app_settings.IMPORT_LIST[0](), "test_method_1")
        self.assertEqual(app_settings.IMPORT_LIST[1](), "test_method_2")

    @override_settings(APP={"IMPORT": "utils.NotExists"})
    def test_import_strings_not_exists(self):
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS, import_strings=self.IMPORT_SETRINGS)
        with self.assertRaises(ImportError):
            app_settings.IMPORT

    @override_settings(APP={"IMPORT_LIST": ["utils.NotExists"]})
    def test_import_strings_not_exists_list(self):
        app_settings = ZeroSettings(key="APP", defaults=self.DEFAULTS, import_strings=self.IMPORT_SETRINGS)
        with self.assertRaises(ImportError):
            app_settings.IMPORT_LIST[0]

    def test_import_strings_not_exists_with_local_user_settings(self):
        user_settings = {"IMPORT": "utils.NotExists"}
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            import_strings=self.IMPORT_SETRINGS,
            user_settings=user_settings,
        )
        with self.assertRaises(ImportError):
            app_settings.IMPORT

    def test_import_strings_not_exists_list_with_local_user_settings(self):
        user_settings = {"IMPORT_LIST": ["utils.NotExists"]}
        app_settings = ZeroSettings(
            key="APP",
            defaults=self.DEFAULTS,
            import_strings=self.IMPORT_SETRINGS,
            user_settings=user_settings,
        )
        with self.assertRaises(ImportError):
            app_settings.IMPORT_LIST[0]

    @override_settings(APP={"REMOVED": "value", "NOT_IN_DEFAULTS": None})
    def test_removed_settings(self):
        defaults = {**self.DEFAULTS, "REMOVED": None, "REMOVED_MSG": "removed"}
        app_settings = ZeroSettings(
            key="APP",
            defaults=defaults,
            removed_settings={
                "REMOVED": None,
                "REMOVED_MSG": "removed",
                "NOT_IN_DEFAULTS": None,
            },
        )
        with self.assertRaisesMessage(AttributeError, "Invalid setting: 'APP.NOT_IN_DEFAULTS'"):
            app_settings.NOT_IN_DEFAULTS

        with self.assertRaisesMessage(RuntimeError, "The 'APP.REMOVED' setting has been removed."):
            app_settings.REMOVED

        with self.assertRaisesMessage(RuntimeError, "removed"):
            app_settings.REMOVED_MSG

    @override_settings(APP={"REMOVED": "value"})
    def test_removed_settings_with_settings_doc(self):
        defaults = {**self.DEFAULTS, "REMOVED": None}
        app_settings = ZeroSettings(
            key="APP",
            defaults=defaults,
            removed_settings={
                "REMOVED": None,
            },
            settings_doc=self.SETTINGS_DOC,
        )
        with self.assertRaisesMessage(
            RuntimeError,
            "The 'APP.REMOVED' setting has been removed. Please refer to '%s' for available settings."
            % (self.SETTINGS_DOC),
        ):
            app_settings.REMOVED

    def test_removed_settings_with_local_user_settings(self):
        user_settings = {"REMOVED": "value", "NOT_IN_DEFAULTS": None}
        defaults = {**self.DEFAULTS, "REMOVED": None, "REMOVED_MSG": "removed"}
        with self.assertRaisesMessage(RuntimeError, "The 'APP.REMOVED' setting has been removed."):
            app_settings = ZeroSettings(
                key="APP",
                defaults=defaults,
                removed_settings={
                    "REMOVED": None,
                    "REMOVED_MSG": "removed",
                    "NOT_IN_DEFAULTS": None,
                },
                user_settings=user_settings,
            )

    def test_removed_settings_with_settings_doc_and_local_user_settings(self):
        user_settings = {"REMOVED": "value"}
        defaults = {**self.DEFAULTS, "REMOVED": None}
        with self.assertRaisesMessage(
            RuntimeError,
            "The 'APP.REMOVED' setting has been removed. Please refer to '%s' for available settings."
            % (self.SETTINGS_DOC),
        ):
            app_settings = ZeroSettings(
                key="APP",
                defaults=defaults,
                removed_settings={
                    "REMOVED": None,
                },
                user_settings=user_settings,
                settings_doc=self.SETTINGS_DOC,
            )
