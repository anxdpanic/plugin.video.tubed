# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import json
from html import unescape

import xbmc  # pylint: disable=import-error

from ..generators.data_cache import get_cached
from ..generators.utils import get_thumbnail
from ..generators.video import video_generator
from ..lib.logger import Log

LOG = Log('dialogs', __file__)


def add_related_video_to_playlist(context, video_id):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    metadata = {}

    if playlist.size() <= 999:
        pages = 0
        add_item = None
        page_token = ''
        current_items = playlist_items(playlist.getPlayListId())

        while not add_item and pages <= 2:
            pages += 1
            try:
                payload = context.api.related_videos(
                    video_id,
                    page_token=page_token,
                    max_results=17,
                    fields='items(kind,id(videoId),snippet(title))'
                )
                result_items = payload.get('items', [])
                page_token = payload.get('nextPageToken', '')

            except:  # pylint: disable=bare-except
                result_items = []

            if result_items:
                add_item = next((
                    item for item in result_items
                    if not any((item.get('id', {}).get('videoId') in playlist_item.get('file') or
                                (unescape(item.get('snippet', {}).get('title', '')) ==
                                 playlist_item.get('label'))) for playlist_item in current_items)),
                    None)

            if not add_item and page_token:
                continue

            if add_item:
                related_id = add_item.get('id', {}).get('videoId')
                cached_payload = get_cached(context, context.api.videos, [related_id])
                cached_video = cached_payload.get(related_id, {})
                cached_snippet = cached_video.get('snippet', {})

                metadata.update({
                    'video_id': related_id,
                    'title': unescape(cached_snippet.get('title', '')),
                    'description': unescape(cached_snippet.get('description', '')),
                    'channel_name': unescape(cached_snippet.get('channelTitle', '')),
                    'thumbnail': get_thumbnail(cached_snippet)
                })

                generated = list(video_generator(context, [add_item]))
                path, list_item, _ = generated[0]
                playlist.add(path, list_item)
                break

            if not page_token:
                break

    return metadata


def playlist_items(playlist_id):
    request = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "Playlist.GetItems",
            "params": {
                "properties": ["title", "file"],
                "playlistid": playlist_id
            },
            "id": 1
        })

    payload = json.loads(xbmc.executeJSONRPC(request))

    if 'result' in payload:
        if 'items' in payload['result']:
            return payload['result']['items']

        return []

    if 'error' in payload:
        message = payload['error']['message']
        code = payload['error']['code']
        error = 'Requested %s and received error %s and code: %s' % (request, message, code)

    else:
        error = 'Requested %s and received error %s' % (request, str(payload))

    LOG.error(error)
    return []
