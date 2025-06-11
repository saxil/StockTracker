"""Stock data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Stock:
    """Stock data model."""
    
    symbol: str
    name: str
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[int] = None
    pe_ratio: Optional[float] = None
    timestamp: Optional[datetime] = None
    
    @property
    def is_gaining(self) -> bool:
        """Check if stock is gaining value."""
        return self.change > 0
    
    @property
    def is_losing(self) -> bool:
        """Check if stock is losing value."""
        return self.change < 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stock to dictionary."""
        return {
            "symbol": self.symbol,
            "name": self.name,
            "current_price": self.current_price,
            "previous_close": self.previous_close,
            "change": self.change,
            "change_percent": self.change_percent,
            "volume": self.volume,
            "market_cap": self.market_cap,
            "pe_ratio": self.pe_ratio,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Stock":
        """Create stock from dictionary."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])
        
        return cls(
            symbol=data["symbol"],
            name=data["name"],
            current_price=data["current_price"],
            previous_close=data["previous_close"],
            change=data["change"],
            change_percent=data["change_percent"],
            volume=data["volume"],
            market_cap=data.get("market_cap"),
            pe_ratio=data.get("pe_ratio"),
            timestamp=timestamp,
        )
