"""Constants for the Microsoft Global Secure Access Version integration."""

DOMAIN = "global_secure_access_version"
MANUFACTURER = "Microsoft"

# URLs
WINDOWS_URL = "https://learn.microsoft.com/en-us/entra/global-secure-access/reference-windows-client-release-history"
MACOS_URL = "https://learn.microsoft.com/en-us/entra/global-secure-access/reference-macos-client-release-history"

# Platforms
PLATFORMS = ["sensor"]

# Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
