"""
Vinted API constants and type definitions.
"""

# Country code to domain mapping
DOMAINS = {
    "fr": "https://www.vinted.fr",
    "de": "https://www.vinted.de",
    "uk": "https://www.vinted.co.uk",
    "pl": "https://www.vinted.pl",
    "es": "https://www.vinted.es",
    "it": "https://www.vinted.it",
    "be": "https://www.vinted.be",
    "nl": "https://www.vinted.nl",
    "at": "https://www.vinted.at",
    "cz": "https://www.vinted.cz",
    "lt": "https://www.vinted.lt",
    "lu": "https://www.vinted.lu",
    "pt": "https://www.vinted.pt",
    "se": "https://www.vinted.se",
    "us": "https://www.vinted.com",
    "ro": "https://www.vinted.ro",
    "gr": "https://www.vinted.gr",
    "hr": "https://www.vinted.hr",
    "hu": "https://www.vinted.hu",
    "sk": "https://www.vinted.sk",
    "si": "https://www.vinted.si",
    "fi": "https://www.vinted.fi",
    "dk": "https://www.vinted.dk",
    "ee": "https://www.vinted.ee",
    "lv": "https://www.vinted.lv",
    "ie": "https://www.vinted.ie"
}


class VintedAPIError(Exception):
    """Raised when Vinted API returns an error."""
    pass


class VintedRateLimitError(Exception):
    """Raised when rate limited by Vinted."""
    pass
