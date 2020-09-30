# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from ..constants import ONE_MONTH
from ..storage.data_cache import DataCache


def get_cached(endpoint, content_ids):
    cache = DataCache()

    payload = {}

    cached_ids = []
    uncached_ids = []

    cached_content = cache.get_items(ONE_MONTH, content_ids)
    for content_id in content_ids:
        if not cached_content.get(content_id):
            uncached_ids.append(content_id)
        else:
            cached_ids.append(content_id)

    payload.update(cached_content)

    if len(uncached_ids) > 0:
        uncached_data = {}

        api_payload = endpoint(uncached_ids)
        items = api_payload.get('items', [])
        for item in items:
            content_id = str(item['id'])
            uncached_data[content_id] = item
            payload[content_id] = item

        cache.set_all(uncached_data)

    return payload
