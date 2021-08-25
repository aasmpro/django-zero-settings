![Tests](https://github.com/aasmpro/django-zero-settings/actions/workflows/tests.yml/badge.svg)
![PYPI](https://github.com/aasmpro/django-zero-settings/actions/workflows/publish.yml/badge.svg)
# Django Zero Settings
a Django util for managing app settings.

when u create a package for Django, usually if your app can be configured, needs to use Django settings. so you will have some defaults which can be overridden by the user.

this package helps you to specify defaults, and the key that users must use for configuring settings, then it will load user settings, update defaults, and import string notations.

this is actually how [django-rest-framework](https://github.com/encode/django-rest-framework/blob/master/rest_framework/settings.py) configures its settings, but with a few more features.

## Install
```
pip install django-zero-settings
```

## Usages
create a settings object like this:
```python
from zero_settings import ZeroSettings

app_settings = ZeroSettings(
    key="APP",
    defaults={
        "TOKEN": "token"
    },
)
```

then you can import `app_settings` and use it:
```python
from app.settings import app_settings

print(app_settings.TOKEN)
```

### Args
`ZeroSettings` can get following args:

| arg                  | desc                                                                                                                                                                                                                                                                                                                                                                                                      |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `key`                | the settings key which users will define settings with, is required and must be a string.                                                                                                                                                                                                                                                                                                                 |
| `defaults`           | default settings for the app, required and must be a dict.                                                                                                                                                                                                                                                                                                                                                |
| `user_settings`      | you can also set user settings manually, in this case, user settings with `key` will not be loaded. is optional and can be a dict.                                                                                                                                                                                                                                                                        |
| `import_strings`     | a list of setting keys that must be imported, import strings is lazy checked and will raise ImportError on exceptions like: `"Could not import 'app.utils.Token' for setting 'APP.TOKEN_CLASS'. ImportError: path does not exist."`                                                                                                                                                                       |
| `removed_settings`   | a dict of settings which had been removed, in `{"KEY": "msg"}` format. it will raise RuntimeError if a setting is in removed_settings. note that these keys must be also on defaults too, otherwise, it will raise AttributeError instead. the `msg` part of dict is the error message. on `None` or empty strings, it generates the default message which is `"The 'APP.KEY' setting has been removed."` |
| `settings_doc`       | a string that locates the settings document path, the value will be used to generate `removed_settings` error with a message like: `"Please refer to 'https://app.com/doc/settings' for available settings."`                                                                                                                                                                                             |
| `use_cache`          | a boolean that defines whether to use cache or not                                                                                                                                                                                                                                                                                                                                                        |
| `strict_defaults`    | a boolean that defines whether to be strict on defaults or not, if true, only default keys are valid in user settings                                                                                                                                                                                                                                                                                     |
| `pre_check_defaults` | a boolean that defines whether to pre check defaults or not                                                                                                                                                                                                                                                                                                                                               |
| `pre_check_imports`  | a boolean that defines whether to pre check imports or not                                                                                                                                                                                                                                                                                                                                                |
| `pre_check_removed`  | a boolean that defines whether to pre check removed or not                                                                                                                                                                                                                                                                                                                                                |


### Import Strings
with following class and methods at `app.utils`:
```python
class Token:
    @staticmethod
    def get_token():
        return "token"

def validate_value(token):
    return token == "token"

def validate_length(token):
    return len(token) == 5
```

you can create an `app_settings` like this:
```python
from zero_settings import ZeroSettings

app_settings = ZeroSettings(
    key="APP",
    defaults={
        "TOKEN_CLASS": "app.utils.Token",
        "TOKEN_VALIDATORS": [
            "app.utils.validate_value",
            "app.utils.validate_length",
        ]
    },
    import_strings=[
        "TOKEN_CLASS",
        "TOKEN_VALIDATORS",
    ]
)
```

then you can import `app_settings` and use it:
```python
from app.settings import app_settings

token = app_setting.TOKEN_CLASS.get_token()
for validator in app_settings.TOKEN_VALIDATORS:
    validator(token)
```

### Removed Settings
removed settings can be configured like:
```python
from zero_settings import ZeroSettings

app_settings = ZeroSettings(
    key="APP",
    defaults={
        "TOKEN": "token",
        "URL": None, # you need to include the key in defaults too.
    },
    removed_settings={
        "URL": None, # or ""
        # or
        "URL": "URL had been removed from settings."
    }
)
```
then if user tries to get the `URL` key, a `RuntimeError` will be raised.


### Cache
ZeroSettings cache results on first attempt to get a key, if `use_cache` is `True`, as it will `setattr` that value to prevent later calls get an `AttributeError` from `__getattribute__`. to prevent this functionality, you can set `use_cache` to `False`.
```python
from zero_settings import ZeroSettings

app_settings = ZeroSettings(
    key="APP",
    defaults={
        "TOKEN": "token"
    },
    use_cache=False
)
```
also there is a `_clear_cache()` method, which let you to clear cache manually. a simple use case can be in tests, when you want cached keys been cleared:
```python
from django.test import TestCase
from django.conf import settings as django_settings
from app.settings import app_settings

@override_settings(APP={"TOKEN": "new_token"})
class MyTestCase(TestCase):
    def test_something(self):
        print(app_settings.TOKEN)                            # new_token
        with self.settings(APP={"TOKEN": "other_token"}):
            app_settings._clear_cache()
            print(django_settings.APP["TOKEN"])              # other_token
            print(app_settings.TOKEN)                        # other_token
            self.assertEqual(django_settings.APP["TOKEN"], app_settings.TOKEN)
```


## Contribution & Tests
Contributions are warmly accepted! change and make it better as you wish.

ZeroSettings use `tox` to run tests for different envs, to run tests:
```
$ pip install tox
$ tox
```
it will create and run tests for following Python and Django versions:
```
Python: 3.5, 3.6, 3.7, 3.8, 3.9
Django: 2.0, 2.2, 3.0, 3.1, 3.2
```