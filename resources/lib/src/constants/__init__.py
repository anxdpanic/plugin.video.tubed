# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from .modes import MODES
from .strings import STRINGS

# the actual constants
__all__ = ['MODES', 'STRINGS']

# the modules containing the constants
__all__ += ['modes', 'strings']
