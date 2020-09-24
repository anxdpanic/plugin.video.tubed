# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from enum import Enum


class MODES(Enum):
    MAIN = 'main'
    MOST_POPULAR = 'most_popular'
    PLAY = 'play'
    RECOMMENDATIONS = 'recommendations'
    SEARCH = 'search'
    MY_CHANNEL = 'my_channel'
    LIKED_VIDEOS = 'liked_videos'
    DISLIKED_VIDEOS = 'disliked_videos'
    PLAYLISTS = 'playlists'
    CHANNELS = 'channels'
    SUBSCRIPTIONS = 'subscriptions'
    LIVE = 'live'
    SIGN_IN = 'sign_in'
    SIGN_OUT = 'sign_out'
    SWITCH_USER = 'switch_user'
    SEARCH_QUERY = 'search_query'

    def __str__(self):
        return str(self.value).lower()
