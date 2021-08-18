## Django Zero Settings
a Django util for managing app settings.
```
pip install django-zero-settings
```

### Usage
you will create a settings object like:
```python
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
```

then you can import it and use:
```python
from app.settings import app_settings

print(app_settings.TEST_KEY)
```

you can register settings for auto reload on change:
```python
from zero_settings import ZeroSettings, register_reload

# create your app settings
app_settings = ZeroSettings(...)

# register app settings
register_reload(app_settings)
```