# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import os

import pyxbmct.addonwindow as pyxbmct  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

from . import DialogActiveException


class RadioButton(pyxbmct.CompareMixin, xbmcgui.ControlRadioButton):

    def __new__(cls, *args, **kwargs):
        kwargs.update({
            'focusOnTexture': os.path.join(pyxbmct.skin.images,
                                           'RadioButton', 'MenuItemFO.png'),
            'noFocusOnTexture': os.path.join(pyxbmct.skin.images,
                                             'RadioButton', 'radiobutton-focus.png'),
            'focusOffTexture': os.path.join(pyxbmct.skin.images,
                                            'RadioButton', 'radiobutton-focus.png'),
            'noFocusOffTexture': os.path.join(pyxbmct.skin.images,
                                              'RadioButton', 'radiobutton-nofocus.png')
        })
        return super(RadioButton, cls).__new__(cls, -10, -10, 1, 1, *args, **kwargs)


# currently required until pyxbmct is updated to remove deprecated textures
pyxbmct.RadioButton = RadioButton


def open_dialog(context, dialog_class):
    try:
        with dialog_class(context=context, window=xbmcgui.Window(10000)) as dialog:
            payload = dialog.start()

    except DialogActiveException:
        payload = None

    except AttributeError:
        payload = None

    return payload
