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
import xbmcgui  # pylint: disable=import-error

from ..generators.video import video_generator
from ..lib.logger import Log
from ..lib.txt_fmt import bold

LOG = Log('scripts', __file__)


def rate(context, video_id, video_title):
    payload = context.api.rating(video_id)
    try:
        payload = payload.get('items', [{}])[0]
    except IndexError:
        return

    rating = payload.get('rating', 'none')

    choices = [
        context.i18n('I like this'),
        context.i18n('I dislike this'),
        context.i18n('Remove rating')
    ]

    choice_map = [
        'like',
        'dislike',
        'none'
    ]

    del choices[choice_map.index(rating)]
    del choice_map[choice_map.index(rating)]

    result = xbmcgui.Dialog().select(context.i18n('Rate'), choices)
    if result == -1:
        return

    rating = choice_map[result]

    payload = context.api.rate(video_id, rating)

    try:
        successful = int(payload.get('error', {}).get('code', 204)) == 204
    except ValueError:
        successful = False

    if successful:
        message = ''

        if video_title:
            video_title = bold(video_title)
            if rating == 'none':
                message = context.i18n('Rating removed from %s') % video_title

            elif rating == 'like':
                message = context.i18n('Liked %s') % video_title

            elif rating == 'dislike':
                message = context.i18n('Disliked %s') % video_title

        else:
            if rating == 'none':
                message = context.i18n('Rating removed')

            elif rating == 'like':
                message = context.i18n('Liked')

            elif rating == 'dislike':
                message = context.i18n('Disliked')

        xbmcgui.Dialog().notification(
            context.addon.getAddonInfo('name'),
            message,
            context.addon.getAddonInfo('icon'),
            sound=False
        )


def add_related_video_to_playlist(context, video_id):
    original_video = video_id
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

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
                video_id = add_item.get('id', {}).get('videoId')
                generated = list(video_generator(context, [add_item]))
                path, list_item, _ = generated[0]
                playlist.add(path, list_item)
                break

            if not page_token:
                break

    if original_video == video_id:
        return None

    return video_id


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
