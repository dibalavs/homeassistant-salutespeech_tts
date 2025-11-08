"""Config flow for Google Translate text-to-speech integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.tts import CONF_LANG
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from homeassistant.const import CONF_API_KEY
from .const import (
    CONF_FORMAT,
    CONF_SAMPLERATE,
    CONF_VALIDATE_SSL,
    CONF_VOICE,
    DEFAULT_FORMAT,
    DEFAULT_LANG,
    DEFAULT_SAMPLERATE,
    DEFAULT_SSL_VALIDATE,
    DEFAULT_VOICE,
    DOMAIN,
    SUPPORT_FORMATS,
    SUPPORT_LANGUAGES,
    SUPPORT_SAMPLERATES,
    CONF_USAGE_TYPE,
    SUPPORT_USAGE_TYPES,
    DEFAULT_USAGE_TYPE,
    CONF_INPUT_TYPE,
    SUPPORT_INPUT_TYPES,
    DEFAULT_INPUT_TYPE,
)

from homeassistant.helpers import config_validation as cv

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(SUPPORT_LANGUAGES),
        vol.Optional(CONF_FORMAT, default=DEFAULT_FORMAT): vol.In(SUPPORT_FORMATS),
        vol.Optional(CONF_SAMPLERATE, default=DEFAULT_SAMPLERATE): vol.In(SUPPORT_SAMPLERATES),
        vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): cv.string, # Do not restrict to SUPPORTED_VOICES because new one can be added
        vol.Optional(CONF_VALIDATE_SSL, default=DEFAULT_SSL_VALIDATE): cv.boolean,
        vol.Optional(CONF_USAGE_TYPE, default=DEFAULT_USAGE_TYPE): vol.In(SUPPORT_USAGE_TYPES),
        vol.Optional(CONF_INPUT_TYPE, default=DEFAULT_INPUT_TYPE): vol.In(SUPPORT_INPUT_TYPES)

    }
)

class SaluteSpeechConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SaluteSpeech text-to-speech."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            self._async_abort_entries_match(
                {
                    CONF_API_KEY: user_input[CONF_API_KEY],
                    CONF_LANG: user_input[CONF_LANG],
                    CONF_FORMAT: user_input[CONF_FORMAT],
                    CONF_SAMPLERATE: user_input[CONF_SAMPLERATE],
                    CONF_VOICE : user_input[CONF_VOICE],
                    CONF_VALIDATE_SSL: user_input[CONF_VALIDATE_SSL],
                    CONF_USAGE_TYPE: user_input[CONF_USAGE_TYPE],
                    CONF_INPUT_TYPE: user_input[CONF_INPUT_TYPE]
                }
            )
            return self.async_create_entry(
                title="Salute Speech text-to-speech", data=user_input
            )

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

    async def async_step_onboarding(
        self, data: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by onboarding."""
        return self.async_create_entry(
            title="Salite Speech text-to-speech",
            data={
                CONF_API_KEY: "",
                CONF_LANG: DEFAULT_LANG,
                CONF_FORMAT: DEFAULT_FORMAT,
                CONF_SAMPLERATE: DEFAULT_SAMPLERATE,
                CONF_VOICE: DEFAULT_VOICE,
                CONF_VALIDATE_SSL: DEFAULT_SSL_VALIDATE,
                CONF_USAGE_TYPE: DEFAULT_USAGE_TYPE,
                CONF_INPUT_TYPE: DEFAULT_INPUT_TYPE
            },
        )
