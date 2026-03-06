"""Core business logic.

Sub-modules are imported on-demand to avoid eager loading of the DB+schema
chain (which requires optional dependencies like email-validator).
Import submodules explicitly:
    from wanderwing.core.matching import MatchingEngine
    from wanderwing.core.experiments import ExperimentTracker
    from wanderwing.core.event_logger import event_logger
"""
