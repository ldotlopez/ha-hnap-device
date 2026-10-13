# HNAP devices for Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://www.hacs.xyz/)
[![Validate with hassfest](https://github.com/ldotlopez/ha-hnap-device/actions/workflows/hassfest.yml/badge.svg)](https://github.com/ldotlopez/ha-hnap-device/actions/workflows/hassfest.yml)
[![Validate with HACS](https://github.com/ldotlopez/ha-hnap-device/actions/workflows/hacs.yml/badge.svg)](https://github.com/ldotlopez/ha-hnap-device/actions/workflows/hacs.yml)
[![GitHub Release](https://img.shields.io/github/v/release/ldotlopez/ha-hnap-device?include_prereleases)](https://github.com/ldotlopez/ha-hnap-device/releases)

This project brings supported HNAP devices into Home Assistant, so you can use
them in your home alongside your other smart devices. Communication takes
place locally on your network; the integration does not rely on a cloud
service. Devices are checked periodically, so updates are polling-based rather
than instantaneous.

Known tested devices:

- D-Link Motion Sensor (DCH-S150)
- D-Link Siren Device (DCH-S220)

The available entities depend on the device: motion sensors provide a motion sensor, and sirens can be controlled from Home Assistant.

## Installation and configuration

1. Install **HNAP device** through [HACS](https://www.hacs.xyz/). If it is not listed, add `ldotlopez/ha-hnap-device` as a custom repository with the **Integration** category.
2. Restart Home Assistant.
3. In Home Assistant, open **Settings > Devices & services**, select **Add integration**, and search for **HNAP device**.
4. Enter the device's network address, username, and password when prompted. Home Assistant will identify the device and add the entities it supports.

Use the username and password configured on the device. The device must be reachable from Home Assistant on the local network.

## Connection status and troubleshooting

If a device becomes unreachable, its device entities show as unavailable while
the integration retries the connection every 30 seconds. The diagnostic
**Connection** binary sensor remains available to show whether communication is
restored. Home Assistant also displays a Repair notification explaining the
connection loss; it is cleared automatically after communication is restored.

If the device remains unavailable, check that it is powered on, reachable from
Home Assistant on the local network, and that its configured credentials are
still valid.

## AI-assisted development

This is a small side project, and the time available to work on it is limited. AI tools are used to assist with some development tasks, but the integration is not developed entirely by AI.
