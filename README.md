# Home Assistant HNAP device component

<!-- HomeAssistant badges -->
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![hassfest validation](https://github.com/ldotlopez/ha-hnap-device/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/ldotlopez/ha-hnap-device/actions/workflows/hassfest.yml)
[![HACS validation](https://github.com/ldotlopez/ha-hnap-device/workflows/Validate%20with%20HACS/badge.svg)](https://github.com/ldotlopez/ha-hnap-device/actions/workflows/hacs.yml)

<!-- Code and releases -->
[![GitHub Release](https://img.shields.io/github/v/release/ldotlopez/ha-hnap-device?include_prereleases)](https://github.com/ldotlopez/ha-hnap-device/releases)
[![CodeQL](https://github.com/ldotlopez/ha-hnap-device/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/ldotlopez/ha-hnap-device/actions/workflows/codeql-analysis.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

<!-- Sponsors -->
<a href="https://www.buymeacoffee.com/zepolson" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 30px !important;width: 105px !important;" ></a>

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
