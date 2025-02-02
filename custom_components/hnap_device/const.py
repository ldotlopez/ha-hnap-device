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


"""Constants for HNAP device integration."""

from hnap import SirenSound

CONF_PLATFORMS = "platforms"
DEFAULT_SIREN_DURATION = 15
DEFAULT_SIREN_TONE = SirenSound.POLICE.name.lower()
DEFAULT_SIREN_VOLUME = 1.0
DEFAULT_USERNAME = "admin"
DOMAIN = "hnap_device"
MAX_FAILURES_BEFORE_UNAVAILABLE = 3
MAX_UPTIME_BEFORE_REBOOT = 60 * 60 * 12  # 12 hours
