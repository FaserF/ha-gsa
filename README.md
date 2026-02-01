[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
![CI](https://github.com/FaserF/ha-gsa/actions/workflows/ci.yml/badge.svg)

# Microsoft Global Secure Access Version Sensor 🔒

This Home Assistant integration tracks the latest available versions of the Microsoft Global Secure Access Client for Windows and macOS by scraping the official Microsoft Learn release notes.

## Features ✨

- **Multi-Platform Support**: Monitors versions for both Windows and macOS.
- **Robust Scraping**: Uses a multi-layered approach to find version information even if the website layout changes slightly.
- **Persistent Failure Detection**: Automatically detects if version information cannot be fetched for a prolonged period.
- **Home Assistant Repairs**: If scraping fails for more than 24 hours, a Repair issue is created in Home Assistant with a link to report the problem on GitHub.
- **Update Notifications Ready**: Easily set up automations to get notified as soon as a new version is released.

## Installation 🛠️

### 1. Using HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed.
2. Go to **HACS** -> **Integrations**.
3. Click the three dots in the top right corner and select **Custom repositories**.
4. Add `https://github.com/FaserF/ha-gsa` with category `Integration`.
5. Click **Add**.
6. Find "Microsoft Global Secure Access Version" and click **Download**.
7. Restart Home Assistant.

### 2. Manual Installation

1. Download the latest release source code.
2. Copy the `custom_components/global_secure_access_version` directory into your Home Assistant's `custom_components` folder.
3. Restart Home Assistant.

## Configuration ⚙️

1. In Home Assistant, go to **Settings** -> **Devices & Services**.
2. Click **Add Integration**.
3. Search for **Microsoft Global Secure Access Version** and follow the prompts.

## Troubleshooting & Repairs 🛠️

### Troubleshooting
If the sensors are showing `Unavailable`, first check your Home Assistant logs. You can enable debug logging for this integration:

```yaml
logger:
  logs:
    custom_components.global_secure_access_version: debug
```

### Repairs Integration
This integration proactively monitors its own health. If Microsoft changes their website layout and the scraping logic fails consistently for **24 hours**, a notification will appear in your **Settings -> Repairs** section. This serves as a clear indicator that the integration needs an update, and it provides a direct link to open a GitHub issue.

## Automation Examples 🚀

Here are some detailed examples of how to use these sensors in your automations. The examples are collapsed in `<details>` blocks to keep the README clean.

<details>
<summary><b>1. Persistent Notification (In Home Assistant)</b></summary>

Creates a notification directly in the Home Assistant sidebar, including the changelog.

```yaml
alias: "GSA: New Version Notification"
description: "Creates a persistent notification for GSA updates"
trigger:
  - platform: state
    entity_id:
      - sensor.gsa_latest_version_windows
      - sensor.gsa_latest_version_macos
condition:
  - condition: template
    value_template: "{{ trigger.from_state.state not in ['unknown', 'unavailable'] }}"
  - condition: template
    value_template: "{{ trigger.to_state.state != trigger.from_state.state }}"
action:
  - service: notify.persistent_notification
    data:
      title: "New GSA Version: {{ trigger.to_state.name }}"
      message: |
        A new version of the Global Secure Access Client is available!

        **Version:** {{ trigger.to_state.state }}
        **Release Date:** {{ state_attr(trigger.entity_id, 'release_day') }}

        **Changelog:**
        {{ state_attr(trigger.entity_id, 'changelog') }}

        [Download / Changelog]({{ state_attr(trigger.entity_id, 'data_provided_by') }})
```
</details>

<details>
<summary><b>2. WhatsApp Notification</b></summary>

Sends an update directly to your phone via WhatsApp.

```yaml
alias: "WhatsApp: GSA Update"
trigger:
  - platform: state
    entity_id: sensor.gsa_latest_version_windows
condition:
  - condition: template
    value_template: "{{ trigger.from_state.state not in ['unknown', 'unavailable'] }}"
action:
  - service: notify.whatsapp_me # Your service name may vary
    data:
      message: "🚀 New Global Secure Access Version for Windows: {{ states('sensor.gsa_latest_version_windows') }} (Date: {{ state_attr('sensor.gsa_latest_version_windows', 'release_day') }})"
```
</details>

<details>
<summary><b>3. Telegram Notification (With HTML Formatting)</b></summary>

Uses HTML for nice formatting including a direct link to the web view.

```yaml
alias: "Telegram: GSA Version Update"
trigger:
  - platform: state
    entity_id: sensor.gsa_latest_version_windows
condition:
  - condition: template
    value_template: "{{ trigger.from_state.state not in ['unknown', 'unavailable'] }}"
action:
  - service: notify.telegram_bot # Your Telegram Notify Service
    data:
      message: |
        <b>🚀 New GSA Windows Update!</b>

        Version: <code>{{ states('sensor.gsa_latest_version_windows') }}</code>
        Date: {{ state_attr('sensor.gsa_latest_version_windows', 'release_day') }}

        <a href="{{ state_attr('sensor.gsa_latest_version_windows', 'data_provided_by') }}">🔗 Open Release Notes</a>
```
</details>

<details>
<summary><b>4. Mobile App Push (iOS/Android)</b></summary>

Native mobile notification that opens the Microsoft release page directly when clicked.

```yaml
alias: "Mobile: GSA Update Alarm"
trigger:
  - platform: state
    entity_id: sensor.gsa_latest_version_windows
action:
  - service: notify.mobile_app_your_phone
    data:
      title: "GSA Update Available"
      message: "Version {{ states('sensor.gsa_latest_version_windows') }} has been released."
      data:
        url: "{{ state_attr('sensor.gsa_latest_version_windows', 'data_provided_by') }}"
        clickAction: "{{ state_attr('sensor.gsa_latest_version_windows', 'data_provided_by') }}"
```
</details>

## Contributions & Issues 🤝
If you encounter any issues or have suggestions, please [open an issue](https://github.com/FaserF/ha-gsa/issues) on GitHub. Contributions are always welcome!

---
*Disclaimer: This integration is not an official Microsoft product. It relies on scraping public documentation.*
