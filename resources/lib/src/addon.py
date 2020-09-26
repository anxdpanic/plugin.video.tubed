# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from .api import API
from .constants import MODES
from .lib.context import Context
from .lib.routing import Router
from .lib.url_utils import parse_query

# pylint: disable=import-outside-toplevel

CONTEXT = Context()

router = Router()


@router.route(MODES.MAIN)
def _main_menu():
    from .routes import main_menu
    main_menu.invoke(CONTEXT)


@router.route(MODES.SIGN_IN)
def _sign_in():
    from .routes import sign_in
    sign_in.invoke(CONTEXT)


@router.route(MODES.SIGN_OUT)
def _sign_out():
    from .routes import sign_out
    sign_out.invoke(CONTEXT)


@router.route(MODES.MANAGE_USERS)
def _manage_users():
    from .routes import manage_users
    manage_users.invoke(CONTEXT)


@router.route(MODES.MOST_POPULAR, kwargs=['page_token'])
def _most_popular(page_token=''):
    from .routes import most_popular
    most_popular.invoke(CONTEXT, page_token=page_token)


@router.route(MODES.LIKED_VIDEOS, kwargs=['page_token'])
def _liked_videos(page_token=''):
    from .routes import liked_videos
    liked_videos.invoke(CONTEXT, page_token=page_token)


@router.route(MODES.DISLIKED_VIDEOS, kwargs=['page_token'])
def _disliked_videos(page_token=''):
    from .routes import disliked_videos
    disliked_videos.invoke(CONTEXT, page_token=page_token)


@router.route(MODES.LIVE, kwargs=['page_token'])
def _live(page_token=''):
    from .routes import live
    live.invoke(CONTEXT, page_token=page_token)


@router.route(MODES.SUBSCRIPTIONS, kwargs=['page_token'])
def _subscriptions(page_token=''):
    from .routes import subscriptions
    subscriptions.invoke(CONTEXT, page_token=page_token)


@router.route(MODES.CHANNEL, args=['channel_id'], kwargs=['page_token'])
def _channel(channel_id, page_token=''):
    # alias of MODES.PLAYLISTS
    from .routes import playlists
    playlists.invoke(CONTEXT, channel_id, page_token=page_token)


@router.route(MODES.PLAYLISTS, args=['channel_id'], kwargs=['page_token'])
def _playlists(channel_id, page_token=''):
    from .routes import playlists
    playlists.invoke(CONTEXT, channel_id, page_token=page_token)


@router.route(MODES.PLAYLIST, args=['playlist_id'], kwargs=['page_token'])
def _playlist(playlist_id, page_token=''):
    from .routes import playlist
    playlist.invoke(CONTEXT, playlist_id, page_token)


@router.route(MODES.PLAY, args=['video_id'])
def _play(video_id):
    from .routes import play
    play.invoke(CONTEXT, video_id=video_id)


@router.route(MODES.SEARCH)
def _search():
    from .routes import search
    search.invoke(CONTEXT)


@router.route(MODES.SEARCH_QUERY, kwargs=['page_token', 'query'])
def _search_query(query='', page_token=''):
    from .routes import search_query
    search_query.invoke(CONTEXT, query, page_token)


@router.route(MODES.MY_CHANNEL, kwargs=['page_token'])
def _my_channel(page_token=''):
    from .routes import my_channel
    my_channel.invoke(CONTEXT, page_token)


def invoke(argv):
    global CONTEXT  # pylint: disable=global-statement

    CONTEXT.argv = argv
    CONTEXT.handle = argv[1]
    CONTEXT.query = parse_query(argv[2])
    CONTEXT.mode = CONTEXT.query.get('mode', 'main')

    CONTEXT.api = API()

    router.invoke(CONTEXT.query)
