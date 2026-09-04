"""Environment-backed settings; paper trading is the only permitted execution mode."""

from functools import lru_cache
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "development"
    database_url: str = "sqlite:///data/ai_trade.db"
    initial_capital: float = Field(10000, gt=0)
    paper_trading_only: bool = True
    max_position_size: float = Field(0.10, gt=0, le=1)
    max_portfolio_risk: float = Field(0.02, gt=0, le=1)
    max_sector_exposure: float = Field(0.25, gt=0, le=1)
    max_drawdown: float = Field(0.15, gt=0, le=1)
    max_open_positions: int = Field(10, gt=0)
    min_risk_reward: float = Field(2.0, gt=0)
    max_correlated_exposure: float = Field(0.30, gt=0, le=1)
    commission_rate: float = Field(0.001, ge=0)
    slippage_rate: float = Field(0.0005, ge=0)
    technical_weight: float = 0.25
    fundamental_weight: float = 0.25
    news_weight: float = 0.15
    macro_weight: float = 0.15
    risk_weight: float = 0.20

    @model_validator(mode="after")
    def paper_only(self):
        if not self.paper_trading_only:
            raise ValueError(
                "Unsafe configuration: PAPER_TRADING_ONLY must remain true; real execution is unsupported."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
