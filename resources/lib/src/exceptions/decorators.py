# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from functools import wraps

import xbmcgui  # pylint: disable=import-error

from ..lib.context import Context
from ..lib.txt_fmt import strip_html


def __api_error_check(payload):
    if isinstance(payload, dict) and 'error' in payload:
        if not ('error' in payload and 'code' in payload['error'] and
                200 <= int(payload['error']['code']) < 300):

            context = Context()
            heading = context.i18n('Error')
            message = ''

            if 'message' in payload['error']:
                message = strip_html(payload['error']['message'])

            if 'errors' in payload['error']:
                error = payload['error']['errors'][0]

                if 'reason' in error:
                    heading += ': ' + error['reason']

                if 'message' in error:
                    message = strip_html(payload['error']['message'])

            if 'code' in payload['error']:
                message = '[%s] %s' % (payload['error']['code'], message)

            xbmcgui.Dialog().notification(
                heading,
                message,
                context.addon.getAddonInfo('icon'),
                sound=False
            )

    return payload


def catch_api_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        payload = func(*args, **kwargs)
        return __api_error_check(payload)

    return wrapper
