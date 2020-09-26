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
        action.ListItem.setArt({
            'icon': 'OverlayLocked.png',
            'thumb': 'OverlayLocked.png'
        })
        items.append(tuple(action))

    directory = Directory(
        label=context.i18n('Most Popular'),
        path=create_addon_path(parameters={
            'mode': str(MODES.MOST_POPULAR)
        })
    )
    directory.ListItem.setArt({
        'icon': 'DefaultTVShows.png',
        'thumb': 'DefaultTVShows.png'
    })
    items.append(tuple(directory))

    directory = Directory(
        label=context.i18n('Categories'),
        path=create_addon_path(parameters={
            'mode': str(MODES.CATEGORIES)
        })
    )
    directory.ListItem.setArt({
        'icon': 'DefaultGenre.png',
        'thumb': 'DefaultGenre.png'
    })
    items.append(tuple(directory))

    if logged_in:
        directory = Directory(
            label=context.i18n('My Channel'),
            path=create_addon_path(parameters={
                'mode': str(MODES.MY_CHANNEL)
            })
        )
        directory.ListItem.setArt({
            'icon': 'DefaultTVShows.png',
            'thumb': 'DefaultTVShows.png'
        })
        items.append(tuple(directory))

        directory = Directory(
            label=context.i18n('Liked Videos'),
            path=create_addon_path(parameters={
                'mode': str(MODES.LIKED_VIDEOS)
            })
        )
        directory.ListItem.setArt({
            'icon': 'DefaultTVShows.png',
            'thumb': 'DefaultTVShows.png'
        })
        items.append(tuple(directory))

        directory = Directory(
            label=context.i18n('Disliked Videos'),
            path=create_addon_path(parameters={
                'mode': str(MODES.DISLIKED_VIDEOS)
            })
        )
        directory.ListItem.setArt({
            'icon': 'DefaultTVShows.png',
            'thumb': 'DefaultTVShows.png'
        })
        items.append(tuple(directory))

        directory = Directory(
            label=context.i18n('Playlists'),
            path=create_addon_path(parameters={
                'mode': str(MODES.PLAYLISTS),
                'channel_id': 'mine'
            })
        )
        directory.ListItem.setArt({
            'icon': 'DefaultVideoPlaylists.png',
            'thumb': 'DefaultVideoPlaylists.png'
        })
        items.append(tuple(directory))

        directory = Directory(
            label=context.i18n('Subscriptions'),
            path=create_addon_path(parameters={
                'mode': str(MODES.SUBSCRIPTIONS)
            })
        )
        directory.ListItem.setArt({
            'icon': 'DefaultStudios.png',
            'thumb': 'DefaultStudios.png'
        })
        items.append(tuple(directory))

    directory = Directory(
        label=context.i18n('Live'),
        path=create_addon_path(parameters={
            'mode': str(MODES.LIVE)
        })
    )
    directory.ListItem.setArt({
        'icon': 'DefaultMovies.png',
        'thumb': 'DefaultMovies.png'
    })
    items.append(tuple(directory))

    directory = Directory(
        label=context.i18n('Search'),
        path=create_addon_path(parameters={
            'mode': str(MODES.SEARCH)
        })
    )
    directory.ListItem.setArt({
        'icon': 'DefaultAddonsSearch.png',
        'thumb': 'DefaultAddonsSearch.png'
    })
    items.append(tuple(directory))

    if logged_in:
        action = Action(
            label=context.i18n('Sign Out'),
            path=create_addon_path(parameters={
                'mode': str(MODES.SIGN_OUT)
            })
        )
        action.ListItem.setArt({
            'icon': 'OverlayLocked.png',
            'thumb': 'OverlayLocked.png'
        })
        items.append(tuple(action))

    action = Action(
        label=context.i18n('Manage Users'),
        path=create_addon_path(parameters={
            'mode': str(MODES.MANAGE_USERS)
        })
    )
    action.ListItem.setArt({
        'icon': 'DefaultUser.png',
        'thumb': 'DefaultUser.png'
    })
    items.append(tuple(action))

    xbmcplugin.addDirectoryItems(context.handle, items, len(items))

    xbmcplugin.endOfDirectory(context.handle, True)
