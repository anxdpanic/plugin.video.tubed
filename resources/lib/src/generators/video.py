# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from copy import deepcopy
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
from ..storage.users import UserStorage
from .data_cache import get_cached
from .data_cache import get_fanart
from .utils import get_thumbnail

WATCH_LATER_PLAYLIST = UserStorage().watchlater_playlist


def video_generator(context, items, mine=False):
    event_type = ''

    if context.mode == str(MODES.LIVE):
        event_type = context.query.get('event_type', '')

    cached_videos = get_cached_videos(context, items, event_type)

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

        context_menus = get_context_menu(context, item, video_id, video_title,
                                         channel_id, channel_name, event_type, mine)

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


def get_cached_videos(context, items, event_type):
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
        parameters = None
        if event_type in ['live', 'completed']:
            parameters = {
                'live_details': True,
            }

        cached_videos = get_cached(
            context,
            context.api.videos,
            [get_id(item) for item in items if get_id(item)],
            parameters,
            cache_ttl=context.settings.data_cache_ttl
        )

    return cached_videos


def get_context_menu(context, item, video_id, video_title,
                     channel_id, channel_name, event_type, mine):
    logged_in = context.api.logged_in

    context_menus = []
    kind = item.get('kind', '')
    snippet = item.get('snippet', {})

    if kind == 'youtube#searchResult' or event_type:
        query = deepcopy(context.query)
        query['order'] = 'prompt'
        context_menus += [
            (context.i18n('Sort order'),
             'Container.Update(%s)' % create_addon_path(query))
        ]

    if logged_in:
        if WATCH_LATER_PLAYLIST and WATCH_LATER_PLAYLIST != snippet.get('playlistId'):
            context_menus += [
                (context.i18n('Add to watch later'),
                 'RunScript(%s,mode=%s&action=add&video_id=%s&playlist_id=%s&playlist_title=%s)' %
                 (ADDON_ID, str(SCRIPT_MODES.PLAYLIST), video_id,
                  WATCH_LATER_PLAYLIST, quote(context.i18n('Watch Later')))),
            ]

        context_menus += [
            (context.i18n('Subscribe'),
             'RunScript(%s,mode=%s&action=add&channel_id=%s&channel_name=%s)' %
             (ADDON_ID, str(SCRIPT_MODES.SUBSCRIPTIONS), channel_id, quote(channel_name))),
        ]

    if event_type != 'upcoming':
        if logged_in:
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
        (context.i18n('Add %s to favorite channels') % bold(channel_name),
         'RunScript(%s,mode=%s&action=add&channel_id=%s&channel_name=%s)' %
         (ADDON_ID, str(SCRIPT_MODES.FAVORITE_CHANNELS), channel_id, quote(channel_name))),

        (context.i18n('Related videos'),
         'Container.Update(plugin://%s/?mode=%s&video_id=%s)' %
         (ADDON_ID, str(MODES.RELATED_VIDEOS), video_id)),

        (context.i18n('Go to %s') % bold(channel_name),
         'Container.Update(plugin://%s/?mode=%s&channel_id=%s)' %
         (ADDON_ID, str(MODES.CHANNEL), channel_id)),

        (context.i18n('Comments'),
         'Container.Update(plugin://%s/?mode=%s&video_id=%s)' %
         (ADDON_ID, str(MODES.COMMENTS_THREADS), video_id)),
    ]

    context_menus += [
        (context.i18n('Refresh'), 'RunScript(%s,mode=%s)' % (ADDON_ID, str(SCRIPT_MODES.REFRESH))),
    ]

    if event_type != 'upcoming':
        context_menus += [
            (context.i18n('Play (Prompt for subtitles)'),
             'PlayMedia(plugin://%s/?mode=%s&video_id=%s&prompt_subtitles=true)' %
             (ADDON_ID, str(MODES.PLAY), video_id)),
        ]

    return context_menus
