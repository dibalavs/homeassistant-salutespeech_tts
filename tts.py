"""Unofficial support for the SaluteSpeech API in TTS integration."""

import aiohttp
import asyncio
import datetime
import logging
import uuid
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from http import HTTPStatus

from homeassistant.components.tts import (
    CONF_LANG,
    PLATFORM_SCHEMA as TTS_PLATFORM_SCHEMA,
    Provider,
    TextToSpeechEntity,
    TtsAudioType
)
from homeassistant.const import CONF_API_KEY
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from typing import Any

from .const import (
    SALUTE_SPEECH_API_URL,
    SBER_OAUTH_URL,
    CONF_FORMAT,
    SUPPORT_FORMATS,
    DEFAULT_FORMAT,
    SUPPORT_FORMATS_TO_FFMPEG,
    CONF_SAMPLERATE,
    SUPPORT_SAMPLERATES,
    DEFAULT_SAMPLERATE,
    CONF_VOICE,
    SUPPORT_VOICES,
    DEFAULT_VOICE,
    SUPPORT_LANGUAGES,
    DEFAULT_LANG,
    CONF_VALIDATE_SSL,
    DEFAULT_SSL_VALIDATE,
    EXPIRATION_GAP,
    SUPPORTED_OPTIONS,
    CONF_USAGE_TYPE,
    SUPPORT_USAGE_TYPES,
    DEFAULT_USAGE_TYPE,
    CONF_INPUT_TYPE,
    SUPPORT_INPUT_TYPES,
    DEFAULT_INPUT_TYPE,
    USAGE_TYPE_TO_SCOPE,
    NULL_DATE
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = TTS_PLATFORM_SCHEMA.extend(
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

async def _get_access_token(hass, sber_key:str, validate_ssl:bool, usage_type:str) -> tuple[str, datetime.datetime]:
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {sber_key}'
    }

    data = { 'scope': USAGE_TYPE_TO_SCOPE[usage_type]}

    websession = async_get_clientsession(hass)

    try:
        async with asyncio.timeout(10):
            request = await websession.post(SBER_OAUTH_URL,
                                            headers=headers,
                                            data = data,
                                            ssl = validate_ssl)

            if request.status != HTTPStatus.OK:
                _LOGGER.error("Error %d on load URL %s", request.status, request.url)
                return ("", NULL_DATE)
            data = await request.json()
            expired = datetime.datetime.fromtimestamp(data.get('expires_at') // 1000) - EXPIRATION_GAP

            return (data.get('access_token'), expired)

    except (TimeoutError, aiohttp.ClientError):
        _LOGGER.error("Timeout for SaluteSpeech TTS API requst")
        return ("", NULL_DATE)


async def _text_to_speech(hass:HomeAssistant,
                          language:str,
                          format:str,
                          voice:str,
                          samplerate:str,
                          token:str,
                          validate_ssl:bool,
                          input_type:str,
                          message:str):
    websession = async_get_clientsession(hass)

    try:
        async with asyncio.timeout(10):
            params = {
                'format': format,
                'voice': f"{voice}_{samplerate}",
                'lang' : language
            }
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': f'application/{input_type}'
            }

            request = await websession.post(SALUTE_SPEECH_API_URL,
                                            headers=headers,
                                            params=params,
                                            data=message.encode('utf-8'),
                                            ssl = validate_ssl)

            if request.status != HTTPStatus.OK:
                _LOGGER.error("Error %d on load URL %s", request.status, request.url)
                return (None, None)
            data = await request.read()

    except (TimeoutError, aiohttp.ClientError):
        _LOGGER.error("Timeout for SaluteSpeech TTS API requst")
        return (None, None)

    return (SUPPORT_FORMATS_TO_FFMPEG[format], data)


async def async_get_engine(hass, config, discovery_info=None):
    """Set up SaluteSpeech component."""
    return SaluteSpeechProvider(hass, config)


class SaluteSpeechProvider(Provider):
    """Set up SaluteSpeech component."""

    def __init__(self, hass, conf):
        """Init TTS service."""
        self.hass = hass
        self._format:str = conf.get(CONF_FORMAT)
        self._key:str = conf.get(CONF_API_KEY)
        self._voice:str = conf.get(CONF_VOICE)
        self._samplerate:str = conf.get(CONF_SAMPLERATE)
        self._language:str = conf.get(CONF_LANG)
        self._validate_ssl:bool = conf.get(CONF_VALIDATE_SSL)
        self._usage_type:str = conf.get(CONF_USAGE_TYPE)
        self._input_type:str = conf.get(CONF_INPUT_TYPE)
        self._token_expiration:datetime.datetime = NULL_DATE
        self._token:str = ""
        self.name = "SaluteSpeech TTS"

    @property
    def default_language(self):
        """Return the default language."""
        return self._language

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return SUPPORT_LANGUAGES

    @property
    def supported_options(self):
        """Return list of supported options."""
        return SUPPORTED_OPTIONS

    async def async_get_tts_audio(self, message, language, options):
        """Load TTS from SaluteSpeech."""

        if datetime.datetime.now() > self._token_expiration:
            self._token, self._token_expiration = await _get_access_token(self.hass, self._key, self._validate_ssl, self._usage_type)

        return await _text_to_speech(
            self.hass,
            self._language,
            self._format,
            self._voice,
            self._samplerate,
            self._token,
            self._validate_ssl,
            self._input_type,
            message)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up SaluteSpeech speech as entity."""
    async_add_entities([SaluteSpeechEntity(hass, config_entry)])


class SaluteSpeechEntity(TextToSpeechEntity):
    """The SaluteSpeech API entity."""

    def __init__(self, hass:HomeAssistant, config_entry: ConfigEntry) -> None:
        """Init SaluteSpeech service."""
        self.hass = hass
        self._format:str = config_entry.data.get(CONF_FORMAT, DEFAULT_FORMAT)
        self._key:str = config_entry.data.get(CONF_API_KEY, "")
        self._voice:str = config_entry.data.get(CONF_VOICE, DEFAULT_VOICE)
        self._samplerate:str = config_entry.data.get(CONF_SAMPLERATE, DEFAULT_SAMPLERATE)
        self._language:str = config_entry.data.get(CONF_LANG, DEFAULT_LANG)
        self._validate_ssl:bool = config_entry.data.get(CONF_VALIDATE_SSL, DEFAULT_SSL_VALIDATE)
        self._usage_type:str = config_entry.data.get(CONF_USAGE_TYPE, DEFAULT_USAGE_TYPE)
        self._input_type:str = config_entry.data.get(CONF_INPUT_TYPE, DEFAULT_INPUT_TYPE)
        self._token_expiration:datetime.datetime = NULL_DATE
        self._token:str = ""

        self._attr_name = f"Salute Speech TTS {self._voice} {self._language}"
        self._attr_unique_id = config_entry.entry_id

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return self._language

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return SUPPORT_LANGUAGES

    @property
    def supported_options(self) -> list[str]:
        """Return a list of supported options."""
        return SUPPORTED_OPTIONS

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        """Load TTS from SaluteSpeech."""
        if datetime.datetime.now() > self._token_expiration:
            self._token, self._token_expiration = await _get_access_token(self.hass, self._key, self._validate_ssl, self._usage_type)

        return await _text_to_speech(
            self.hass,
            self._language,
            self._format,
            self._voice,
            self._samplerate,
            self._token,
            self._validate_ssl,
            self._input_type,
            message)
