# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""


def get_thumbnail(snippet):
    thumbnails = snippet.get('thumbnails', {})
    thumbnail = thumbnails.get('standard', thumbnails.get('high', {}))

    if not thumbnail:
        thumbnail = thumbnails.get('medium', thumbnails.get('default', {}))

    return thumbnail.get('url', '')


def get_fanart(branding_settings):
    banners = branding_settings.get('image', {})
    banner = banners.get('bannerTvImageUrl', banners.get('bannerTvHighImageUrl', ''))

    if not banner:
        banner = banners.get('bannerTvMediumImageUrl', banners.get('bannerTvLowImageUrl', ''))

    return banner
