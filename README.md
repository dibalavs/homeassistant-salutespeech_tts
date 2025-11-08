# SaluteSpeechTTS Integration for Home Assistant

## Overview

This project provides unofficial support for SaluteSpeech TTS integration for Home Assistant. It allows you to use `configuration.yaml` to configure TTS with legacy provider support and new GUI-style configuration with config flow.

## Installation

1. Navigate to your Home Assistant custom components directory:
    ```bash
    <homeassistant_config_directory>/custom_components/
    ```
2. Clone the repository:
    ```bash
    git clone https://github.com/dibalavs/homeassistant-salutespeech_tts.git salutespeech_tts
    ```
3. Restart Home Assistant

## Configuration

This integration supports both YAML configuration and GUI-based configuration via config flow.

### YAML Configuration (legacy style)

```yaml
tts:
  - platform: salutespeech_tts
    api_key: "asdavaadfasdf" # required.
    format: "opus" # optional. allowed: ["wav16", "pcm16", "opus"]. default "opus"
    samplerate: "24000" # optional. allowed: ["8000", "24000"]. default: "24000"
    voice: "Nec" # optional. allowed: ["Nec", "Bys", "May", "Tur", "Ost", "Pon", "Kin"] default: "Ost"
    language: "ru" # optional. allowed: ["ru", "uz", "pt", "pl", "nl", "kz", "en", "de", "es", "fr", "it", "ky"] default "ru"
    validate_ssl: "no" # optional. Use "yes" if you have installed Mintsifry certificate. otherwise - "no"
    usage_type: "personal" # optional. allowed: ["personal", "corp", "b2b"]. default "personal"
    input_type: "text" # optional. allowed: ["text", "ssml"]. default: "text"
```

[How to get free API key (in Russian)](https://developers.sber.ru/docs/ru/salutespeech/quick-start/integration-individuals)
[List of supported launguages (in Russian)](https://developers.sber.ru/docs/ru/salutespeech/guides/synthesis/ssml/language)

### GUI Configuration (Config Flow)

- Go to  Settings > Devices & Services.
- In the bottom right corner, select the  Add Integration button.
- From the list, select Salute Speech.
- Follow the instructions on screen to complete the setup.

## Usage Examples

### Legacy Style TTS Action

```yaml
# Example of a script or automation action
- service: tts.salutespeech_tts_say
  data:
    message: "Привет, мир!"
    entity_id: media_player.your_media_player # Replace with your media player entity
```

### New Entity-Based TTS Action

```yaml
# Example of a script or automation action using an entity
- service: tts.speak
  target:
    entity_id: tts.salutespeech_tts # The entity created by configuration with GUI
  data:
    message: "Hello, world!"
    media_player_entity_id: media_player.your_media_player # Replace with your media player entity
