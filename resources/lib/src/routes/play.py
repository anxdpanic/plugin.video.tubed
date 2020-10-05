# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from html import unescape

import arrow
import xbmc  # pylint: disable=import-error
import xbmcplugin  # pylint: disable=import-error

from ..api.utils import choose_subtitles
from ..generators.data_cache import get_cached
from ..generators.utils import get_thumbnail
from ..items.stream import Stream


def invoke(context, video_id, prompt_subtitles=False):
    quality = context.api.quality(
        context.settings.video_quality,
        limit_30fps=context.settings.limit_to_30fps,
        hdr=context.settings.hdr
    )

    payload = context.api.resolve(video_id=video_id, quality=quality)

    try:
        cached_payload = get_cached(context, context.api.videos, [video_id])
    except:  # pylint: disable=bare-except
        cached_payload = {}

    license_data = payload.get('license', {})

    resolved_metadata = payload.get('metadata', {})
    resolved_channel = resolved_metadata.get('channel', {})
    resolved_video = resolved_metadata.get('video', {})
    resolved_images = resolved_metadata.get('images', {})

    thumbnail = resolved_images.get('standard', resolved_images.get('high', ''))
    if not thumbnail:
        thumbnail = resolved_images.get('medium', resolved_images.get('default', ''))

    cached_video = cached_payload.get(video_id, {})
    snippet = cached_video.get('snippet', {})

    if not snippet:
        video_title = resolved_video.get('title', '')
        channel_name = resolved_channel.get('author', '')

    else:
        video_title = unescape(snippet.get('title', ''))
        channel_name = unescape(snippet.get('channelTitle', ''))

    stream = Stream(
        label=video_title,
        label2=channel_name,
        path=payload.get('url', ''),
        headers=payload.get('headers', ''),
        license_key=license_data.get('proxy', '')
    )

    subtitles = choose_subtitles(
        context,
        subtitles=resolved_metadata.get('subtitles', []),
        prompt_override=prompt_subtitles
    )
    stream.ListItem.setSubtitles(subtitles)

    if snippet:
        published_arrow = arrow.get(snippet['publishedAt']).to('local')
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

        stream.ListItem.setInfo('video', info_labels)

        thumbnail = get_thumbnail(snippet)

    stream.ListItem.setArt({
        'icon': thumbnail,
        'thumb': thumbnail,
    })

    if context.handle != -1:
        xbmcplugin.setResolvedUrl(context.handle, True, stream.ListItem)

    else:
        xbmc.Player().play(item=stream.ListItem.getPath(), listitem=stream.ListItem)
