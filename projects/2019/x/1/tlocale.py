#!/usr/bin/env python

import locale
from datetime import datetime, timezone
import time


locs = locale.setlocale(locale.LC_ALL)
locg = locale.getlocale()

print("set", locs)
"""
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

dt = datetime.now(timezone.utc)
dt_str = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")
print(dt_str)

lt = time.localtime()
print(lt)

loc = locale.setlocale(locale.LC_TIME, 'pt-BR')
print("set", loc)
locs = locale.setlocale(locale.LC_ALL)
print("set", locs)

print(time.tzname)

dt = datetime.now(timezone.utc)
dt_str = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")
print(dt_str)
