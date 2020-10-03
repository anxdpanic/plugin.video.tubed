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
from ..lib.txt_fmt import bold
from ..lib.url_utils import create_addon_path
from .data_cache import get_cached
from .data_cache import get_fanart
from .utils import get_thumbnail


def playlist_generator(context, items):
    cached_playlists = get_cached(
        context.api.playlists,
        [get_id(item) for item in items if get_id(item)],
        cache_ttl=context.settings.data_cache_ttl
    )

    fanart = get_fanart(
        context.api.channels,
        [item.get('snippet', {}).get('channelId')
         for item in items if item.get('snippet', {}).get('channelId')],
        cache_ttl=context.settings.data_cache_ttl
    )

    is_mine = context.query.get('channel_id', '') == 'mine'

    for item in items:
        playlist_id = get_id(item)

        if not playlist_id:
            continue

        playlist = cached_playlists.get(playlist_id, item)
        snippet = playlist.get('snippet', {})

        channel_id = snippet.get('channelId', '')
        channel_name = unescape(snippet.get('channelTitle', ''))

        playlist_title = unescape(snippet.get('title', ''))

        payload = Directory(
            label=playlist_title,
            label2=channel_name,
            path=create_addon_path({
                'mode': str(MODES.PLAYLIST),
                'playlist_id': playlist_id,
                'mine': str(is_mine).lower()
            })
        )

        info_labels = {
            'plot': unescape(snippet.get('description', '')),
            'plotoutline': unescape(snippet.get('description', '')),
            'originaltitle': playlist_title,
            'sorttitle': playlist_title,
            'studio': channel_name
        }
        payload.ListItem.setInfo('video', info_labels)

        thumbnail = get_thumbnail(snippet)

        payload.ListItem.setArt({
            'icon': thumbnail,
            'thumb': thumbnail,
            'fanart': fanart.get(channel_id, ''),
        })

        context_menus = []

        if not is_mine:
            context_menus += [
                (context.i18n('Subscribe'),
                 'RunScript(%s,mode=%s&action=add&channel_id=%s&channel_name=%s)' %
                 (ADDON_ID, str(SCRIPT_MODES.SUBSCRIPTIONS), channel_id, quote(channel_name))),

                (context.i18n('Go to %s') % bold(unescape(snippet.get('channelTitle', ''))),
                 'Container.Update(plugin://%s/?mode=%s&channel_id=%s)' %
                 (ADDON_ID, str(MODES.CHANNEL), channel_id))
            ]

        if is_mine:
            context_menus += [
                (context.i18n('Rename playlist'),
                 'RunScript(%s,mode=%s&action=rename&playlist_id=%s&playlist_title=%s)' %
                 (ADDON_ID, str(SCRIPT_MODES.PLAYLIST), playlist_id, quote(playlist_title))),

                (context.i18n('Delete playlist'),
                 'RunScript(%s,mode=%s&action=delete&playlist_id=%s&playlist_title=%s)' %
                 (ADDON_ID, str(SCRIPT_MODES.PLAYLIST), playlist_id, quote(playlist_title)))
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
