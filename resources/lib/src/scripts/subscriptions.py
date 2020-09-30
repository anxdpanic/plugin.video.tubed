# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

from ..lib.memoizer import reset_cache


def invoke(context, action):
    if action == 'add':
        channel_id = context.query.get('channel_id', '')
        if not channel_id:
            return

        payload = context.api.subscribe(channel_id)

        try:
            successful = int(payload.get('error', {}).get('code', 204)) == 204
        except ValueError:
            successful = False

        if successful:
            xbmcgui.Dialog().notification(
                context.addon.getAddonInfo('name'),
                context.i18n('Subscribed'),
                context.addon.getAddonInfo('icon'),
                sound=False
            )

            reset_cache()

    elif action == 'remove':
        subscription_id = context.query.get('subscription_id', '')
        if not subscription_id:
            return

        payload = context.api.unsubscribe(subscription_id)

        try:
            successful = int(payload.get('error', {}).get('code', 204)) == 204
        except ValueError:
            successful = False

        if successful:
            xbmcgui.Dialog().notification(
                context.addon.getAddonInfo('name'),
                context.i18n('Unsubscribed'),
                context.addon.getAddonInfo('icon'),
                sound=False
            )

            xbmc.executebuiltin('Container.Refresh')
            reset_cache()
