from collections import namedtuple
from .settings import ZeroSettings, register_reload


VersionInfo = namedtuple("VersionInfo", ("major", "minor", "patch"))

VERSION = VersionInfo(0, 0, 0)

__version__ = "{0.major}.{0.minor}.{0.patch}".format(VERSION)
__all__ = [ZeroSettings, register_reload]
