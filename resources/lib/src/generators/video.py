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
from ..items.video import Video
from ..lib.url_utils import create_addon_path
from .data_cache import get_cached


def video_generator(context, items):
    cached_videos = \
        get_cached(context.api.videos, [get_id(item) for item in items if get_id(item)])

    for item in items:
        video_id = get_id(item)

        if not video_id:
            continue

        video = cached_videos.get(video_id, item)

        snippet = video.get('snippet', {})
        if not snippet:
            continue

        channel_id = snippet.get('channelId', '')

        payload = Video(
            label=unescape(snippet.get('title', '')),
            label2=unescape(snippet.get('channelTitle', '')),
            path=create_addon_path({
                'mode': str(MODES.PLAY),
                'video_id': video_id
            })
        )

        info_labels = {
            'mediatype': 'video',
            'plot': unescape(snippet.get('description', '')),
            'plotoutline': unescape(snippet.get('description', '')),
            'originaltitle': unescape(snippet.get('title', '')),
            'sorttitle': unescape(snippet.get('title', '')),
            'studio': unescape(snippet.get('channelTitle', ''))
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
             'RunScript(%s,mode=%s&action=add&channel_id=%s)' %
             (ADDON_ID, str(SCRIPT_MODES.SUBSCRIPTIONS), channel_id)),
        ]

        payload.ListItem.addContextMenuItems(context_menus)
        yield tuple(payload)


def get_id(item):
    kind = item.get('kind', '')
    if kind == 'youtube#video':
        return item.get('id', '')

    if kind == 'youtube#playlistItem':
        return item.get('snippet', {}).get('resourceId', {}).get('videoId', '')

    if kind == 'youtube#searchResult':
        if isinstance(item.get('id', {}), dict):
            return item.get('id', {}).get('videoId', '')

    return ''
