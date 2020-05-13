#!/usr/bin/env python

import locale
from datetime import datetime, timezone
import time


"""
locg = locale.getlocale()
print("get", locg)

loc = locale.getlocale(locale.LC_COLLATE)
print(loc)

loc = locale.getlocale(locale.LC_CTYPE)
print(loc)

loc = locale.getlocale(locale.LC_MONETARY)
print(loc)

loc = locale.getlocale(locale.LC_MONETARY)
print(loc)

loc = locale.getlocale(locale.LC_TIME)
print(loc)
"""

locs = locale.setlocale(locale.LC_ALL)
print("set", locs)

dt = datetime.now(timezone.utc)

dt_str = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")
print(dt_str)

loc = locale.getlocale(locale.LC_CTYPE)
print(loc)
(lang_code, encoding) = loc
print(lang_code, encoding)
lang_code = lang_code.replace("_", "-")
print(lang_code, encoding)

locs = locale.setlocale(locale.LC_TIME, lang_code)
locs = locale.setlocale(locale.LC_ALL)
print("set", locs)

dt = datetime.now(timezone.utc)
dt_str = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")
print(dt_str)

print(time.altzone)
print(time.daylight)
print(time.timezone)
print(time.tzname)

lt = time.localtime()
print(lt)
print(lt.tm_zone, lt.tm_gmtoff)
