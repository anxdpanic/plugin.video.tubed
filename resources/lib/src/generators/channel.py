# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from html import unescape
from urllib.parse import quote

from ..constants import ADDON_ID
from ..constants import MODES
from ..constants import SCRIPT_MODES
from ..items.directory import Directory
from ..lib.url_utils import create_addon_path
from .data_cache import get_cached
from .utils import get_thumbnail


def channel_generator(context, items):
    cached_channels = \
        get_cached(context.api.channels, [get_id(item) for item in items if get_id(item)])

    for item in items:
        channel_id = get_id(item)

        if not channel_id:
            continue

        channel = cached_channels.get(channel_id, item)
        snippet = channel.get('snippet', {})

        channel_name = unescape(snippet.get('channelTitle', ''))

        payload = Directory(
            label=unescape(snippet.get('title', '')),
            label2=channel_name,
            path=create_addon_path({
                'mode': str(MODES.CHANNEL),
                'channel_id': channel_id
            })
        )

        info_labels = {
            'plot': unescape(snippet.get('description', '')),
            'plotoutline': unescape(snippet.get('description', '')),
            'originaltitle': unescape(snippet.get('title', '')),
            'sorttitle': unescape(snippet.get('title', '')),
            'studio': channel_name
        }
        payload.ListItem.setInfo('video', info_labels)

        thumbnail = get_thumbnail(snippet)

        payload.ListItem.setArt({
            'icon': thumbnail,
            'thumb': thumbnail,
        })

        context_menus = [
            (context.i18n('Subscribe'),
             'RunScript(%s,mode=%s&action=add&channel_id=%s&channel_name=%s)' %
             (ADDON_ID, str(SCRIPT_MODES.SUBSCRIPTIONS), channel_id, quote(channel_name))),
        ]

        payload.ListItem.addContextMenuItems(context_menus)
        yield tuple(payload)


def get_id(item):
    kind = item.get('kind', '')
    if kind == 'youtube#channel':
        return item.get('id', '')

    if kind == 'youtube#searchResult':
        return item.get('id', {}).get('channelId')

    return ''
