# Home Assistant HNAP device component

![hassfest validation](https://github.com/ldotlopez/ha-hnap-device/workflows/Validate%20with%20hassfest/badge.svg)
![HACS validation](https://github.com/ldotlopez/ha-hnap-device/workflows/Validate%20with%20HACS/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

This is a *Work in Progress* integration to Home Assistant supporting HNAP devices. It communicates locally with the devices, i.e. no cloud needed, but only supports polling.

Theorically all HNAP devices are supported, however only a few are really tested:

  * D-Link Motion Sensor (DCH-S150)
  * D-Link Siren Device (DCH-S220)

Currently motion sensors and sirens are the only platforms implemented but support for cameras or water detectors are really easy to implemented.

This integration uses modern features from HomeAssistant like UI config.

See [https://github.com/ldotlopez/python-hnap](https://github.com/ldotlopez/python-hnap)

Special thanks to other projects:

  * https://github.com/mtflud/DCH-S220-Web-Control
  * https://github.com/postlund/dlink_hnap
