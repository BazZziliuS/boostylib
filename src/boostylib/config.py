"""Configuration for BoostyClient via pydantic-settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

try:
    from pydantic_settings import TomlConfigSettingsSource

    _HAS_TOML = True
except ImportError:
    _HAS_TOML = False


class BoostySettings(BaseSettings):
    """Boosty client configuration.

    All fields can be overridden via:
    - Environment variables with ``BOOSTY_`` prefix (e.g. ``BOOSTY_TIMEOUT=10``)
    - TOML config file ``boosty.toml`` (requires ``tomli`` / Python 3.11+)
    - Constructor arguments
    """

    model_config = SettingsConfigDict(
        env_prefix="BOOSTY_",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customise settings sources to include TOML configuration if available.

        Args:
            settings_cls: BaseSettings class.
            init_settings: Init settings source.
            env_settings: Environment variables settings source.
            dotenv_settings: Dotenv settings source.
            file_secret_settings: File secret settings source.

        Returns:
            Tuple of prioritized settings sources.
        """
        sources: list[PydanticBaseSettingsSource] = [
            init_settings,
            env_settings,
        ]
        if _HAS_TOML:
            sources.append(TomlConfigSettingsSource(settings_cls, toml_file="boosty.toml"))
        sources.append(file_secret_settings)
        return tuple(sources)

    # API
    base_url: str = "https://api.boosty.to/v1"
    timeout: float = 30.0

    # Retry
    max_retries: int = 3
    retry_backoff_factor: float = 0.5

    # Rate limiting
    rate_limit_requests: int = 60
    rate_limit_period: float = 60.0

    # Polling
    poll_interval: float = 30.0

    # Auth
    token_refresh_margin: int = 300  # seconds before expiry to trigger refresh

    # Cache
    cache_enabled: bool = True
    cache_ttl_blog: int = 300
    cache_ttl_levels: int = 600
    cache_ttl_user: int = 120
    cache_ttl_default: int = 60

    # Debug
    debug: bool = False
