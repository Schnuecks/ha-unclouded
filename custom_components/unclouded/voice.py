"""Work out whether the voice assistant keeps working without the internet.

An Assist pipeline turns speech into text, lets a conversation agent act on it and
speaks the answer. Each of these stages can run locally or through a cloud service;
if one needs the internet, voice control does not work during an outage.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .analyze import Analyzer, Source, async_build_analyzer, worst
from .classify import Reach

# The built-in agent that understands commands without any service.
BUILT_IN_AGENT = "conversation.home_assistant"
# Where the voice assistant keeps its pipelines in hass.data.
ASSIST_PIPELINE = "assist_pipeline"
# What a satellite's pipeline select shows while it follows the preferred pipeline.
PREFERRED = "preferred"


@dataclass(slots=True)
class Stage:
    """One step of a pipeline."""

    # "wake_word", "stt", "conversation" or "tts".
    kind: str
    engine: str
    reach: Reach
    # Stable key of the reason; the panel turns it into text.
    reason: str
    entry_id: str | None = None


@dataclass(slots=True)
class PipelineReport:
    """Verdict for one Assist pipeline."""

    id: str
    name: str
    preferred: bool
    # Worst stage; local or internal means voice control keeps working.
    reach: Reach
    stages: list[Stage] = field(default_factory=list)
    # Voice satellites using this pipeline, by device name.
    satellites: list[str] = field(default_factory=list)


def _engine_reach(analyzer: Analyzer, engine: str) -> Source:
    """Reach of an STT, TTS or conversation engine.

    Current engines are entities; older providers are named after their integration,
    e.g. "cloud".
    """
    if "." in engine:
        return analyzer.entity_reach(engine)
    return analyzer.integration_reach(engine)


def _conversation(analyzer: Analyzer, engine: str, local_first: bool) -> Stage:
    if engine == BUILT_IN_AGENT:
        return Stage("conversation", engine, Reach.LOCAL, "built_in_agent")
    reach, reason, entry_id = _engine_reach(analyzer, engine)
    # Commands the built-in agent understands still work; questions do not.
    if reach is Reach.CLOUD and local_first:
        reach, reason = Reach.PARTIAL, "agent_local_first"
    return Stage("conversation", engine, reach, reason, entry_id)


def _satellites(hass: HomeAssistant) -> dict[str, list[str]]:
    """Device names by the pipeline they use, preferred under PREFERRED."""
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    result: dict[str, list[str]] = {}
    for entry in ent_reg.entities.values():
        if entry.domain != "select" or not entry.unique_id.endswith("-pipeline"):
            continue
        if entry.disabled_by or (state := hass.states.get(entry.entity_id)) is None:
            continue
        device = dev_reg.async_get(entry.device_id) if entry.device_id else None
        name = (device and (device.name_by_user or device.name)) or state.name
        result.setdefault(state.state, []).append(name)
    return result


async def async_analyze_voice(hass: HomeAssistant) -> list[PipelineReport]:
    """Analyze every Assist pipeline of this instance."""
    # Read by its key: importing the voice assistant would load all of it.
    if (data := hass.data.get(ASSIST_PIPELINE)) is None:
        return []
    store = data.pipeline_store
    preferred = store.async_get_preferred_item()
    analyzer = await async_build_analyzer(hass)
    satellites = _satellites(hass)

    reports = []
    for pipeline in store.data.values():
        stages = []
        if pipeline.wake_word_entity:
            stages.append(
                Stage(
                    "wake_word",
                    pipeline.wake_word_entity,
                    *analyzer.entity_reach(pipeline.wake_word_entity),
                )
            )
        if pipeline.stt_engine:
            stages.append(
                Stage(
                    "stt",
                    pipeline.stt_engine,
                    *_engine_reach(analyzer, pipeline.stt_engine),
                )
            )
        stages.append(
            _conversation(
                analyzer,
                pipeline.conversation_engine,
                bool(getattr(pipeline, "prefer_local_intents", False)),
            )
        )
        if pipeline.tts_engine:
            stages.append(
                Stage(
                    "tts",
                    pipeline.tts_engine,
                    *_engine_reach(analyzer, pipeline.tts_engine),
                )
            )
        is_preferred = pipeline.id == preferred
        users = satellites.get(pipeline.name, [])
        if is_preferred:
            users = users + satellites.get(PREFERRED, [])
        reach = worst((s.reach, s.reason, s.entry_id) for s in stages)[0]
        reports.append(
            PipelineReport(
                id=pipeline.id,
                name=pipeline.name,
                preferred=is_preferred,
                reach=reach,
                stages=stages,
                satellites=sorted(users),
            )
        )
    return sorted(reports, key=lambda r: (not r.preferred, r.name))
