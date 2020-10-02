# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

from ..lib.txt_fmt import bold
from ..storage.users import UserStorage

USERS = UserStorage()


def invoke(context):
    data = context.api.request_codes()
    interval = int(data.get('interval', 5)) * 1000
    if interval > 60000:
        interval = 5000

    device_code = data['device_code']
    user_code = data['user_code']
    verification_url = data.get('verification_url', 'google.com/device').lstrip('https://www.')

    message = context.i18n('Go to %s and enter the following code:') % bold(verification_url)
    message += ' ' + bold(user_code)

    dialog = xbmcgui.DialogProgress()
    dialog.create(heading=context.i18n('Sign In'), message=message)

    steps = ((10 * 60 * 1000) // interval)  # 10 Minutes
    for index in range(steps):
        dialog.update(int(float((100.0 // steps)) * index))

        signed_in = context.api.request_access_token(device_code)
        if signed_in:
            dialog.close()
            break

        if dialog.iscanceled():
            dialog.close()
            break

        xbmc.sleep(interval)

    dialog.close()

    xbmc.executebuiltin('Container.Refresh')
