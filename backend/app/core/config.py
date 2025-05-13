from functools import lru_cache

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, YamlConfigSettingsSource


class AppSettings(BaseSettings):
	environment: str = "dev"
	port: int = 5000
	log_level: str = "DEBUG"

	# embedding model
	embedding_model: str = "all-MiniLM-L6-v2"

	# vector db
	chroma_host: str = "chromadb"
	chroma_port: int = 8000
	chroma_collection: str = "pdf_chunks"

	# .ENV
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_app_settings() -> AppSettings:
	return AppSettings()


class LLMConfiguration(BaseModel):
	name: str
	provider: str
	model: str
	api_key: SecretStr


class LLMSettings(BaseSettings):
	llms: list[LLMConfiguration]

	model_config = SettingsConfigDict(yaml_file="llm_providers.yaml", extra="ignore")

	@classmethod
	def settings_customise_sources(
		cls,
		settings_cls: type[BaseSettings],
		init_settings: PydanticBaseSettingsSource,
		env_settings: PydanticBaseSettingsSource,
		dotenv_settings: PydanticBaseSettingsSource,
		file_secret_settings: PydanticBaseSettingsSource,
	) -> tuple[PydanticBaseSettingsSource, ...]:
		return (YamlConfigSettingsSource(settings_cls),)


@lru_cache
def get_llm_settings() -> LLMSettings:
	return LLMSettings()  # type: ignore[call-arg]
