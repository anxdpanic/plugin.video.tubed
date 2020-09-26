# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmcplugin  # pylint: disable=import-error

from ..constants import MODES
from ..items.action import Action
from ..items.directory import Directory
from ..lib.url_utils import create_addon_path


def invoke(context):
    items = []

    logged_in = context.api.logged_in

    if not logged_in:
        action = Action(
            label=context.i18n('Sign In'),
            path=create_addon_path(parameters={
                'mode': str(MODES.SIGN_IN)
            })
        )
        items.append(tuple(action))

    if logged_in:
        directory = Directory(
            label=context.i18n('Recommendations'),
            path=create_addon_path(parameters={
                'mode': str(MODES.RECOMMENDATIONS)
            })
        )
        items.append(tuple(directory))

    directory = Directory(
        label=context.i18n('Most Popular'),
        path=create_addon_path(parameters={
            'mode': str(MODES.MOST_POPULAR)
        })
    )
    items.append(tuple(directory))

    if logged_in:
        directory = Directory(
            label=context.i18n('My Channel'),
            path=create_addon_path(parameters={
                'mode': str(MODES.MY_CHANNEL)
            })
        )
        items.append(tuple(directory))

        directory = Directory(
            label=context.i18n('Liked Videos'),
            path=create_addon_path(parameters={
                'mode': str(MODES.LIKED_VIDEOS)
            })
        )
        items.append(tuple(directory))

        directory = Directory(
            label=context.i18n('Disliked Videos'),
            path=create_addon_path(parameters={
                'mode': str(MODES.DISLIKED_VIDEOS)
            })
        )
        items.append(tuple(directory))

        directory = Directory(
            label=context.i18n('Playlists'),
            path=create_addon_path(parameters={
                'mode': str(MODES.PLAYLISTS)
            })
        )
        items.append(tuple(directory))

        directory = Directory(
            label=context.i18n('Subscriptions'),
            path=create_addon_path(parameters={
                'mode': str(MODES.SUBSCRIPTIONS)
            })
        )
        items.append(tuple(directory))

    directory = Directory(
        label=context.i18n('Live'),
        path=create_addon_path(parameters={
            'mode': str(MODES.LIVE)
        })
    )
    items.append(tuple(directory))

    directory = Directory(
        label=context.i18n('Search'),
        path=create_addon_path(parameters={
            'mode': str(MODES.SEARCH)
        })
    )
    items.append(tuple(directory))

    if logged_in:
        action = Action(
            label=context.i18n('Sign Out'),
            path=create_addon_path(parameters={
                'mode': str(MODES.SIGN_OUT)
            })
        )
        items.append(tuple(action))

    action = Action(
        label=context.i18n('Manage Users'),
        path=create_addon_path(parameters={
            'mode': str(MODES.MANAGE_USERS)
        })
    )
    items.append(tuple(action))

    xbmcplugin.addDirectoryItems(context.handle, items, len(items))

    xbmcplugin.endOfDirectory(context.handle, True)
