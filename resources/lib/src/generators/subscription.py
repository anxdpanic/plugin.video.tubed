# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from html import unescape

from ..constants import ADDON_ID
from ..constants import MODES
from ..constants import SCRIPT_MODES
from ..items.directory import Directory
from ..lib.url_utils import create_addon_path
from .data_cache import get_cached


def subscription_generator(context, items):
    cached_channels = \
        get_cached(context.api.channels, [get_id(item) for item in items if get_id(item)])

    for item in items:
        channel_id = get_id(item)

        if not channel_id:
            continue

        subscription_id = item.get('id', '')

        channel = cached_channels.get(channel_id, item)
        snippet = channel.get('snippet', {})

        payload = Directory(
            label=unescape(snippet.get('title', '')),
            path=create_addon_path({
                'mode': str(MODES.PLAYLISTS),
                'channel_id': channel_id
            })
        )

        info_labels = {
            'plot': unescape(snippet.get('description', '')),
            'plotoutline': unescape(snippet.get('description', '')),
            'originaltitle': unescape(snippet.get('title', '')),
            'sorttitle': unescape(snippet.get('title', '')),
            'studio': unescape(snippet.get('title', ''))
        }
        payload.ListItem.setInfo('video', info_labels)

        thumbnails = snippet.get('thumbnails', {})
        thumbnail = thumbnails.get('standard', thumbnails.get('high', {}))
        if not thumbnail:
            thumbnail = thumbnails.get('medium', thumbnails.get('default', {}))
        thumbnail = thumbnail.get('url', '')

        payload.ListItem.setArt({
            'icon': thumbnail,
            'thumb': thumbnail,
        })

        context_menus = [
            (context.i18n('Unsubscribe'),
             'RunScript(%s,mode=%s&action=remove&subscription_id=%s)' %
             (ADDON_ID, str(SCRIPT_MODES.SUBSCRIPTIONS), subscription_id)),
        ]

        payload.ListItem.addContextMenuItems(context_menus)
        yield tuple(payload)


def get_id(item):
    snippet = item.get('snippet', {})
    return snippet.get('resourceId', {}).get('channelId', snippet.get('channelId', ''))
