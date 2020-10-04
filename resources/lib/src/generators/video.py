# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from html import unescape
from urllib.parse import quote

import arrow

from ..constants import ADDON_ID
from ..constants import MODES
from ..constants import SCRIPT_MODES
from ..items.action import Action
from ..items.video import Video
from ..lib.txt_fmt import bold
from ..lib.url_utils import create_addon_path
from .data_cache import get_cached
from .data_cache import get_fanart
from .utils import get_thumbnail


def video_generator(context, items, mine=False):
    event_type = ''

    if context.mode == str(MODES.LIVE):
        event_type = context.query.get('event_type', '')

    if event_type == 'upcoming':
        # don't add upcoming video items to long term cache since
        # they will change when in progress or completed
        cached_videos = {}

        videos = context.api.videos(
            [get_id(item) for item in items if get_id(item)],
            live_details=True
        )

        for video in videos.get('items', []):
            cached_videos[get_id(video)] = video

    else:
        cached_videos = get_cached(
            context,
            context.api.videos,
            [get_id(item) for item in items if get_id(item)],
            cache_ttl=context.settings.data_cache_ttl
        )

    fanart = get_fanart(
        context,
        context.api.channels,
        [item.get('snippet', {}).get('channelId')
         for _, item in cached_videos.items()
         if item.get('snippet', {}).get('channelId')],
        cache_ttl=context.settings.data_cache_ttl
    )

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

        published_arrow = None
        scheduled_start = None
        live_details = video.get('liveStreamingDetails')

        if live_details:
            actual_start = live_details.get('actualStartTime')
            actual_end = live_details.get('actualEndTime')
            scheduled_start = live_details.get('scheduledStartTime')

            published = actual_end or actual_start or scheduled_start
            if published:
                published_arrow = arrow.get(published).to('local')

        if not published_arrow:
            published_arrow = arrow.get(snippet['publishedAt']).to('local')

        if event_type == 'upcoming':
            payload = Action(
                label=video_title,
                label2=channel_name,
                path=create_addon_path({
                    'mode': str(MODES.UPCOMING_NOTIFICATION),
                    'title': quote(video_title),
                    'timestamp': scheduled_start
                })
            )
        else:
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
            'studio': channel_name,
            'year': published_arrow.year,
            'premiered': published_arrow.format('YYYY-MM-DD'),
            'dateadded': published_arrow.format('YYYY-MM-DD HH:mm:ss'),
        }

        if snippet.get('liveBroadcastContent', 'none') != 'none':
            info_labels['playcount'] = 0

        payload.ListItem.setInfo('video', info_labels)

        thumbnail = get_thumbnail(snippet)

        payload.ListItem.setArt({
            'icon': thumbnail,
            'thumb': thumbnail,
            'fanart': fanart.get(channel_id, ''),
        })

        context_menus = [
            (context.i18n('Subscribe'),
             'RunScript(%s,mode=%s&action=add&channel_id=%s&channel_name=%s)' %
             (ADDON_ID, str(SCRIPT_MODES.SUBSCRIPTIONS), channel_id, quote(channel_name))),
        ]

        if event_type != 'upcoming':
            context_menus += [
                (context.i18n('Rate'),
                 'RunScript(%s,mode=%s&video_id=%s&video_title=%s)' %
                 (ADDON_ID, str(SCRIPT_MODES.RATE), video_id, quote(video_title))),

                (context.i18n('Add to playlist'),
                 'RunScript(%s,mode=%s&action=add&video_id=%s)' %
                 (ADDON_ID, str(SCRIPT_MODES.PLAYLIST), video_id)),
            ]

            if mine and 'snippet' in item and 'playlistId' in item['snippet']:
                context_menus += [
                    (context.i18n('Remove from playlist'),
                     'RunScript(%s,mode=%s&action=remove&playlistitem_id=%s&video_title=%s)' %
                     (ADDON_ID, str(SCRIPT_MODES.PLAYLIST), item['id'], quote(video_title)))
                ]

        context_menus += [
            (context.i18n('Related videos'),
             'Container.Update(plugin://%s/?mode=%s&video_id=%s)' %
             (ADDON_ID, str(MODES.RELATED_VIDEOS), video_id)),

            (context.i18n('Go to %s') % bold(unescape(snippet.get('channelTitle', ''))),
             'Container.Update(plugin://%s/?mode=%s&channel_id=%s)' %
             (ADDON_ID, str(MODES.CHANNEL), channel_id)),

            (context.i18n('Comments'),
             'Container.Update(plugin://%s/?mode=%s&video_id=%s)' %
             (ADDON_ID, str(MODES.COMMENTS_THREADS), video_id)),
        ]

        if event_type != 'upcoming':
            context_menus += [
                (context.i18n('Play (Prompt for subtitles)'),
                 'RunScript(%s,mode=%s&video_id=%s&prompt_subtitles=true)' %
                 (ADDON_ID, str(SCRIPT_MODES.PLAY), video_id)),
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
