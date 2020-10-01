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
        channel_name = unescape(snippet.get('channelTitle', ''))

        video_title = unescape(snippet.get('title', ''))

        payload = Video(
            label=video_title,
            label2=channel_name,
            path=create_addon_path({
                'mode': str(MODES.PLAY),
                'video_id': video_id
            })
        )

        info_labels = {
            'mediatype': 'video',
            'plot': unescape(snippet.get('description', '')),
            'plotoutline': unescape(snippet.get('description', '')),
            'originaltitle': video_title,
            'sorttitle': video_title,
            'studio': channel_name
        }

        if snippet.get('liveBroadcastContent', 'none') != 'none':
            info_labels['playcount'] = 0

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
            (context.i18n('Play (Prompt for subtitles)'),
             'RunScript(%s,mode=%s&video_id=%s&prompt_subtitles=true)' %
             (ADDON_ID, str(SCRIPT_MODES.PLAY), video_id)),

            (context.i18n('Subscribe'),
             'RunScript(%s,mode=%s&action=add&channel_id=%s&channel_name=%s)' %
             (ADDON_ID, str(SCRIPT_MODES.SUBSCRIPTIONS), channel_id, quote(channel_name))),

            (context.i18n('Rate'),
             'RunScript(%s,mode=%s&video_id=%s&video_title=%s)' %
             (ADDON_ID, str(SCRIPT_MODES.RATE), video_id, quote(video_title))),

            (context.i18n('Go to %s') % unescape(snippet.get('channelTitle', '')),
             'Container.Update(plugin://%s/?mode=%s&channel_id=%s)' %
             (ADDON_ID, str(MODES.CHANNEL), channel_id)),
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
