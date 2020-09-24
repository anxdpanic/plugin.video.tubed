# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from functools import wraps

from .api import V3Exception


def __api_error_check(payload):
    if 'error' in payload:
        raise V3Exception(payload)

    return payload


def catch_api_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        payload = func(*args, **kwargs)
        return __api_error_check(payload)

    return wrapper
