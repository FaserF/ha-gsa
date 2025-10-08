[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
# Global Secure Access Client version Homeassistant Sensor
The `global_secure_access_version` sensor will give you a sensor with the latest version available.

## Installation
### 1. Using HACS (recommended way)

This integration is no official HACS Integration and right now an custom integration.

Open HACS then install the "Microsoft Global Secure Access Version" integration or use the link below.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=FaserF&repository=ha-gsa&category=integration)

If you use this method, your component will always update to the latest version.

### 2. Manual

- Download the latest zip release from [here](https://github.com/FaserF/ha-gsa/releases/latest)
- Extract the zip file
- Copy the folder "gsa" from within custom_components with all of its components to `<config>/custom_components/`

where `<config>` is your Home Assistant configuration directory.

>__NOTE__: Do not download the file by using the link above directly, the status in the "master" branch can be in development and therefore is maybe not working.

## Configuration

Go to Configuration -> Integrations and click on "add integration". Then search for "Microsoft Global Secure Access Version".

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=gsa)

### Configuration Variables
None needed.

## Automations
```yaml
- id: 'gsa_new_version_notification_windows'
  alias: 'GSA: New Version Available for Windows'
  description: 'Notifies when the GSA version sensor changes to a valid state.'
  trigger:
    - platform: state
      entity_id: sensor.global_secure_access_client_windows
  condition:
    - condition: template
      value_template: "{{ trigger.to_state.state not in ['unknown', 'unavailable'] }}"
    - condition: template
      value_template: "{{ trigger.from_state.state not in ['unknown', 'unavailable'] }}"
    - condition: template
      value_template: "{{ trigger.to_state.state != trigger.from_state.state }}"
  action:
    - service: notify.mobile_app_your_device
      data:
        title: '🎉 New GSA Version Available for Windows!'
        message: >
          New version **{{ trigger.to_state.state }}** is now available!
          (Previous version: {{ trigger.from_state.state }})
        data:
          url: "[https://learn.microsoft.com/en-us/entra/global-secure-access/reference-windows-client-release-history](https://learn.microsoft.com/en-us/entra/global-secure-access/reference-windows-client-release-history)"
  mode: single
```

## Bug reporting
Open an issue over at [github issues](https://github.com/FaserF/ha-gsa/issues). Please prefer sending over a log with debugging enabled.

To enable debugging enter the following in your configuration.yaml

```yaml
logger:
    logs:
        custom_components.global_secure_access_version: debug
```

You can then find the log in the HA settings -> System -> Logs -> Enter "global_secure_access_version" in the search bar -> "Load full logs"

## Thanks to
The data is coming from the corresponding [Microsoft Learn](https://learn.microsoft.com/en-us/entra/global-secure-access/reference-windows-client-release-history) website.
