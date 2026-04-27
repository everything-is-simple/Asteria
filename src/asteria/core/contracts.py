from __future__ import annotations

from enum import Enum


class ModuleStatus(str, Enum):
    DRAFT = "draft"
    FROZEN = "frozen"
    BUILDING = "building"
    VERIFYING = "verifying"
    RELEASED = "released"
    INTEGRATED = "integrated"
    BLOCKED = "blocked"


class MainlineModule(str, Enum):
    MALF = "malf"
    ALPHA = "alpha"
    SIGNAL = "signal"
    POSITION = "position"
    PORTFOLIO_PLAN = "portfolio_plan"
    TRADE = "trade"
    SYSTEM = "system"
