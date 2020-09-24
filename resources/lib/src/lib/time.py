# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import datetime
import time


def strptime(timestamp, timestamp_format):
    import _strptime  # pylint: disable=import-outside-toplevel
    try:
        time.strptime('01 01 2012', '%d %m %Y')
    finally:
        return time.strptime(timestamp, timestamp_format)  # pylint: disable=lost-exception


def now():
    # now that always has microseconds
    _now = datetime.datetime.now()

    try:
        _ = datetime.datetime(*(strptime(_now.strftime('%Y-%m-%d %H:%M:%S.%f'),
                                         '%Y-%m-%d %H:%M:%S.%f')[0:6]))
        return _now
    except:  # pylint: disable=bare-except
        return _now + datetime.timedelta(microseconds=1)


def timestamp_diff(timestamp=None):
    if not timestamp:
        return 86400

    try:
        then = datetime.datetime(*(strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')[0:6]))
    except ValueError:
        then = datetime.datetime(*(strptime(timestamp, '%Y-%m-%d %H:%M:%S')[0:6]))
    except TypeError:
        return 604800

    delta = now() - then

    return delta.total_seconds()
