"""HIL test scenario schema and management."""

from .schema import (
    FaultType,
    SatelliteConfig,
    FaultInjection,
    SuccessCriteria,
    Scenario,
    load_scenario,
    validate_scenario,
    SCENARIO_SCHEMA,
)
from .parser import (
    ScenarioExecutor,
    execute_scenario_file,
    run_scenario_file,
)

__all__ = [
    "FaultType",
    "SatelliteConfig",
    "FaultInjection",
    "SuccessCriteria",
    "Scenario",
    "load_scenario",
    "validate_scenario",
    "SCENARIO_SCHEMA",
    "ScenarioExecutor",
    "execute_scenario_file",
    "run_scenario_file",
]
