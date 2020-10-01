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
from .lib.routing import Router
from .lib.url_utils import parse_script_query

# pylint: disable=import-outside-toplevel

CONTEXT = Context()

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


@router.route(SCRIPT_MODES.PLAY, args=['video_id'])
def _play(video_id):
    from .scripts import play
    play.invoke(CONTEXT, video_id=video_id)


def invoke(argv):
    global CONTEXT  # pylint: disable=global-statement

    CONTEXT.argv = argv
    CONTEXT.handle = -1

    try:
        CONTEXT.query = parse_script_query(CONTEXT.argv[1])
    except IndexError:
        CONTEXT.query = parse_script_query('')

    CONTEXT.mode = CONTEXT.query.get('mode', str(SCRIPT_MODES.MAIN))

    CONTEXT.api = API(
        language=CONTEXT.settings.language,
        region=CONTEXT.settings.region
    )

    router.invoke(CONTEXT.query)
