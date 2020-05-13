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

def f(h):
    return ((h > 0) - (h < 0)) * (abs(h) % 24)

h = -13
print(h, f(h))

h = -12
print(h, f(h))

h = -11
print(h, f(h))

h = -1
print(h, f(h))

h = 0
print(h, f(h))

h = 1
print(h, f(h))

h = 11
print(h, f(h))

h = 12
print(h, f(h))

h = 13
print(h, f(h))
# Get local time zone
lt = time.localtime() # localtime returns tm_gmtoff in seconds
gmt_min_off = (int(abs(lt.tm_gmtoff) / 60)) % 60
h = lt.tm_gmtoff // 3600
gmt_hours_off = ((h > 0) - (h < 0)) * (abs(h) % 24)


# Set database timezone
print(f"SET TIME ZONE INTERVAL \'{gmt_hours_off:+03}:{gmt_min_off:02}\' HOUR TO MINUTE")
"""

# Set locale
loc = locale.getlocale(locale.LC_CTYPE)
(language_code, encoding ) = loc
language_code = language_code.replace("_", "-", 1)
locale.setlocale(locale.LC_TIME, language_code)
print(loc, language_code, encoding)

