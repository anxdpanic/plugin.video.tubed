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


def playlist_generator(context, items):
    cached_playlists = \
        get_cached(context.api.playlists, [get_id(item) for item in items if get_id(item)])

    for item in items:
        playlist_id = get_id(item)

        if not playlist_id:
            continue

        playlist = cached_playlists.get(playlist_id, item)
        snippet = playlist.get('snippet', {})

        channel_id = snippet.get('channelId', '')
        channel_name = unescape(snippet.get('channelTitle', ''))

        payload = Directory(
            label=unescape(snippet.get('title', '')),
            label2=channel_name,
            path=create_addon_path({
                'mode': str(MODES.PLAYLIST),
                'playlist_id': playlist_id
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
            (context.i18n('Subscribe'),
             'RunScript(%s,mode=%s&action=add&channel_id=%s&channel_name=%s)' %
             (ADDON_ID, str(SCRIPT_MODES.SUBSCRIPTIONS), channel_id, quote(channel_name))),

            (context.i18n('Go to %s') % unescape(snippet.get('channelTitle', '')),
             'Container.Update(plugin://%s/?mode=%s&channel_id=%s)' %
             (ADDON_ID, str(MODES.CHANNEL), channel_id)),
        ]

        payload.ListItem.addContextMenuItems(context_menus)

        yield tuple(payload)


def get_id(item):
    kind = item.get('kind', '')
    if kind == 'youtube#playlist':
        return item.get('id', '')

    if kind == 'youtube#searchResult':
        return item.get('id', {}).get('playlistId', '')

    return ''
