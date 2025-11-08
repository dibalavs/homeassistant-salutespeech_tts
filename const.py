import datetime
from homeassistant.components.tts import CONF_LANG

DOMAIN = "salutespeech_tts"

# SaluteSpeech API endpoints
SALUTE_SPEECH_API_URL = "https://smartspeech.sber.ru/rest/v1/text:synthesize"
SBER_OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

CONF_FORMAT = "format"
SUPPORT_FORMATS = [
    "wav16",
    "pcm16",
    "opus",
   # "alaw", ### ERROR: ffmpeg does not recognize it
   # "g729"  ### ERROR: ffmpeg does not recognize it
]
DEFAULT_FORMAT = "opus"

SUPPORT_FORMATS_TO_FFMPEG = {
    "wav16": "wav",
    "pcm16": "s16le",  # raw signed 16-bit little-endian PCM
    "opus" : "ogg",
    "alaw" : "alaw",  # Unsupported by ffmpeg in this environment
    "g729" : "g729"  # Unsupported by ffmpeg in this environment
}

CONF_SAMPLERATE = "samplerate"
SUPPORT_SAMPLERATES = ["8000", "24000"]
DEFAULT_SAMPLERATE = "24000"

CONF_VOICE = "voice"
SUPPORT_VOICES = ["Nec", "Bys", "May", "Tur", "Ost", "Pon", "Kin"]
DEFAULT_VOICE = "Ost"

SUPPORT_LANGUAGES = ["ru", "uz", "pt", "pl", "nl", "kz", "en", "de", "es", "fr", "it", "ky"]
DEFAULT_LANG = "ru"

CONF_VALIDATE_SSL = "validate_ssl"
DEFAULT_SSL_VALIDATE = "false"

CONF_USAGE_TYPE = "usage_type"
SUPPORT_USAGE_TYPES = ["personal", "corp", "b2b"]
DEFAULT_USAGE_TYPE = "personal"
USAGE_TYPE_TO_SCOPE = {
    "personal": "SALUTE_SPEECH_PERS",
    "corp": "SALUTE_SPEECH_CORP",
    "b2b": "SALUTE_SPEECH_B2B",
}

CONF_INPUT_TYPE = "input_type"
SUPPORT_INPUT_TYPES = ["text", "ssml"]
DEFAULT_INPUT_TYPE = "text"

EXPIRATION_GAP = datetime.timedelta(seconds=30)
NULL_DATE = datetime.datetime(1970, 1, 1)

SUPPORTED_OPTIONS = [CONF_LANG, CONF_FORMAT, CONF_VOICE, CONF_SAMPLERATE, CONF_VALIDATE_SSL]
