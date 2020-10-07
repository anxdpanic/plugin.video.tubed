# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from .api import API
from .constants import SCRIPT_MODES
from .lib.context import Context
from .lib.logger import Log
from .lib.routing import Router
from .lib.url_utils import parse_script_query

# pylint: disable=import-outside-toplevel

CONTEXT = Context()
LOG = Log('entrypoint', __file__)

router = Router()


@router.route(SCRIPT_MODES.MAIN)
def _main():
    CONTEXT.addon.openSettings()  # TODO: possibly replace with configuration wizard


@router.route(SCRIPT_MODES.SEARCH_HISTORY, args=['action'], kwargs=['item'])
def _search_history(action, item=''):
    from .scripts import search_history
    search_history.invoke(CONTEXT, action, item)


@router.route(SCRIPT_MODES.CONFIGURE_REGIONAL)
def _configure_regional():
    from .scripts import configure_regional
    configure_regional.invoke(CONTEXT)


@router.route(SCRIPT_MODES.CONFIGURE_SUBTITLES)
def _configure_subtitles():
    from .scripts import configure_subtitles
    configure_subtitles.invoke(CONTEXT)


@router.route(SCRIPT_MODES.SUBSCRIPTIONS, args=['action'],
              kwargs=['channel_id', 'subscription_id', 'channel_name'])
def _subscriptions(action, channel_id='', subscription_id='', channel_name=''):
    from .scripts import subscriptions
    subscriptions.invoke(CONTEXT, action, channel_id, subscription_id, channel_name)


@router.route(SCRIPT_MODES.RATE, args=['video_id'], kwargs=['video_title'])
def _rate(video_id, video_title=''):
    from .scripts import rate
    rate.invoke(CONTEXT, video_id, video_title)


@router.route(SCRIPT_MODES.CONFIGURE_PLAYLISTS,
              args=['action', 'playlist_type', 'playlist_id'], kwargs=['playlist_title'])
def _configure_playlists(action, playlist_type, playlist_id, playlist_title=''):
    from .scripts import configure_playlists
    configure_playlists.invoke(CONTEXT, action, playlist_type, playlist_id, playlist_title)


@router.route(SCRIPT_MODES.READ_COMMENT, kwargs=['thread_id', 'comment_id'])
def _read_comment(thread_id='', comment_id=''):
    from .scripts import read_comment
    read_comment.invoke(CONTEXT, thread_id, comment_id)


@router.route(SCRIPT_MODES.PLAYLIST, args=['action'],
              kwargs=['video_id', 'video_title', 'playlist_id',
                      'playlist_title', 'playlistitem_id'])
def _playlist(action, video_id='', video_title='', playlist_id='',
              playlist_title='', playlistitem_id=''):
    from .scripts import playlist
    playlist.invoke(CONTEXT, action, video_id, video_title, playlist_id,
                    playlist_title, playlistitem_id)


@router.route(SCRIPT_MODES.CACHE, args=['action', 'cache_type'])
def _cache(action, cache_type):
    from .scripts import cache
    cache.invoke(CONTEXT, action, cache_type)


@router.route(SCRIPT_MODES.POST_PLAY, args=['video_id'], kwargs=['position'])
def _post_play(video_id, position=-1):
    from .scripts import post_play
    post_play.invoke(CONTEXT, video_id, position)


@router.route(SCRIPT_MODES.PLAY, args=['video_id'], kwargs=['prompt_subtitles'])
def _play(video_id, prompt_subtitles=False):
    from .scripts import play
    play.invoke(CONTEXT, video_id, prompt_subtitles)


def invoke(argv):
    global CONTEXT  # pylint: disable=global-statement

    CONTEXT.argv = argv
    CONTEXT.handle = -1

    try:
        CONTEXT.query = parse_script_query(CONTEXT.argv[1])
    except IndexError:
        CONTEXT.query = parse_script_query('')

    CONTEXT.mode = CONTEXT.query.get('mode', str(SCRIPT_MODES.MAIN))

    LOG.debug(
        'Invoker:\n  Handle: %s\n  Mode: %s\n  Parameters: %s\n' %
        (str(CONTEXT.handle), CONTEXT.mode, CONTEXT.query)
    )

    CONTEXT.api = API(
        language=CONTEXT.settings.language,
        region=CONTEXT.settings.region
    )

    router.invoke(CONTEXT.query)
