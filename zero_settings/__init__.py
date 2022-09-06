from collections import namedtuple
from .settings import ZeroSettings


VersionInfo = namedtuple("VersionInfo", ("major", "minor", "patch"))

VERSION = VersionInfo(0, 1, 11)

__version__ = "{0.major}.{0.minor}.{0.patch}".format(VERSION)
__all__ = [ZeroSettings]
