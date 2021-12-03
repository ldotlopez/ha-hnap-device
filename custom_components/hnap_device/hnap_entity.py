# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.


class HNapEntity:
    def __init__(self, info, api, unique_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._attr_unique_id = unique_id
        self._attr_device_info = {
            "identifiers": {
                ("mac", api.info["DeviceMacId"]),
            },
            "manufacturer": api.info["VendorName"],
            "model": api.info["ModelName"],
            "name": api.info["DeviceName"],
        }
        self._attr_name = self._attr_device_info["name"]

        self._api = api
