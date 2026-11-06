"""Tests for the analysis of the voice assistant."""

from types import SimpleNamespace

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.unclouded.classify import Reach
from custom_components.unclouded.voice import async_analyze_voice


def _pipeline(pid: str, name: str, **engines) -> SimpleNamespace:
    return SimpleNamespace(
        id=pid,
        name=name,
        wake_word_entity=engines.get("wake"),
        stt_engine=engines.get("stt"),
        conversation_engine=engines.get("agent", "conversation.home_assistant"),
        tts_engine=engines.get("tts"),
        prefer_local_intents=engines.get("local_first", False),
    )


def _store(hass: HomeAssistant, pipelines: list, preferred: str) -> None:
    store = SimpleNamespace(
        data={p.id: p for p in pipelines}, async_get_preferred_item=lambda: preferred
    )
    hass.data["assist_pipeline"] = SimpleNamespace(pipeline_store=store)


def _entity(hass: HomeAssistant, domain: str, object_id: str, entry, **kw) -> str:
    return (
        er.async_get(hass)
        .async_get_or_create(
            domain,
            entry.domain,
            kw.pop("unique_id", object_id),
            suggested_object_id=object_id,
            config_entry=entry,
            **kw,
        )
        .entity_id
    )


async def test_no_voice_assistant(hass: HomeAssistant) -> None:
    """Without the voice assistant there is nothing to report."""
    assert await async_analyze_voice(hass) == []


async def test_local_and_cloud_pipelines(hass: HomeAssistant) -> None:
    """Every stage is classified; the worst stage decides."""
    wyoming = MockConfigEntry(domain="wyoming", title="Whisper")
    cloud = MockConfigEntry(domain="cloud", title="Home Assistant Cloud")
    for entry in (wyoming, cloud):
        entry.add_to_hass(hass)
    whisper = _entity(hass, "stt", "whisper", wyoming)
    piper = _entity(hass, "tts", "piper", wyoming)
    cloud_stt = _entity(hass, "stt", "cloud", cloud)
    _store(
        hass,
        [
            _pipeline("a", "Local", stt=whisper, tts=piper),
            _pipeline("b", "Cloud", stt=cloud_stt, tts=piper),
        ],
        preferred="b",
    )

    first, second = await async_analyze_voice(hass)

    # The preferred pipeline comes first.
    assert (first.name, first.preferred, first.reach) == ("Cloud", True, Reach.CLOUD)
    assert first.stages[0].entry_id == cloud.entry_id
    assert (second.name, second.reach) == ("Local", Reach.LOCAL)
    assert [s.kind for s in second.stages] == ["stt", "conversation", "tts"]
    assert second.stages[1].reason == "built_in_agent"


async def test_cloud_agent(hass: HomeAssistant) -> None:
    """A cloud agent stops voice control, unless commands are handled locally first."""
    llm = MockConfigEntry(domain="openai_conversation", title="ChatGPT")
    llm.add_to_hass(hass)
    agent = _entity(hass, "conversation", "chatgpt", llm)
    _store(
        hass,
        [
            _pipeline("a", "LLM", agent=agent),
            _pipeline("b", "LLM local first", agent=agent, local_first=True),
        ],
        preferred="a",
    )

    first, second = await async_analyze_voice(hass)

    assert first.reach is Reach.CLOUD
    assert (second.reach, second.stages[0].reason) == (
        Reach.PARTIAL,
        "agent_local_first",
    )


async def test_legacy_provider_and_satellites(hass: HomeAssistant) -> None:
    """Older engines are named after their integration; satellites are listed."""
    esphome = MockConfigEntry(domain="esphome", title="Kitchen")
    esphome.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=esphome.entry_id, identifiers={("esphome", "k")}, name="Kitchen"
    )
    select = _entity(
        hass,
        "select",
        "kitchen_pipeline",
        esphome,
        unique_id="k-pipeline",
        device_id=device.id,
    )
    hass.states.async_set(select, "preferred")
    # A legacy provider is a loaded integration without entities.
    hass.config.components.add("google_translate")
    _store(hass, [_pipeline("a", "Default", tts="google_translate")], preferred="a")

    (report,) = await async_analyze_voice(hass)

    assert report.stages[-1].reach is Reach.CLOUD
    assert report.satellites == ["Kitchen"]
