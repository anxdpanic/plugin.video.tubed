# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from html import unescape

import xbmc  # pylint: disable=import-error

from ..generators.data_cache import get_cached
from ..lib.memoizer import reset_cache
from ..lib.utils import wait_for_busy_dialog
from ..storage.users import UserStorage
from .utils import add_related_video_to_playlist
from .utils import rate


def invoke(context, video_id, position=-1):
    users = UserStorage()
    if not post_play(context, users):
        return

    try:
        position = int(position)
    except ValueError:
        position = -1

    try:
        video = get_cached(context, context.api.videos, [video_id]).get(video_id, {})
    except:  # pylint: disable=bare-except
        video = {}

    video_title = unescape(video.get('snippet', {}).get('title', ''))

    if context.settings.post_play_rate:
        rate(context, video_id, video_title)

    if context.settings.autoplay_related:
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        if position > -1:
            start_position = position + 1
            video_id = add_related_video_to_playlist(context, video_id)

            if video_id and start_position < playlist.size():
                safe = wait_for_busy_dialog()
                if safe:
                    xbmc.Player().play(item=playlist, startpos=start_position)

    if users.history_playlist:
        try:
            _ = context.api.add_to_playlist(users.history_playlist, video_id)
        except:  # pylint: disable=bare-except
            pass

    if users.watchlater_playlist:
        try:
            playlist_item_id = \
                context.api.video_id_to_playlist_item_id(users.watchlater_playlist, video_id)

            if playlist_item_id:
                _ = context.api.remove_from_playlist(playlist_item_id)
        except:  # pylint: disable=bare-except
            pass

    reset_cache()


def post_play(context, users):
    if context.settings.post_play_rate:
        return True

    if context.settings.autoplay_related:
        return True

    if users.history_playlist:
        return True

    if users.watchlater_playlist:
        return True

    return False
