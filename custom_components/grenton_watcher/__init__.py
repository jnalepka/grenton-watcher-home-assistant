import logging
import aiohttp
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)
DOMAIN = "grenton_watcher"

def normalize_value(value):
    if value is None:
        return None
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, (list, set, tuple)):
        return ",".join(
            str(v.value if hasattr(v, "value") else v)
            for v in value
        )
    if isinstance(value, (int, float)):
        return value
    return str(value)

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    api_endpoint = entry.data["api_endpoint"]
    mappings = entry.options.get("mappings", [])

    entity_ids = list({m["entity_id"] for m in mappings})

    @callback
    async def state_changed(event):
        new_state = event.data.get("new_state")
        if not new_state:
            return

        command = {}
        counter = 1
        for m in mappings:
            if new_state.entity_id == m["entity_id"]:
                attr = m.get("attribute")
                raw_value = new_state.state if attr == "state" else new_state.attributes.get(attr)
                
                feature=m["name"]
                val=normalize_value(raw_value)
                
                add_index = "" if counter == 1 else f"_{counter}"
                counter += 1
                if '->' in feature:
                    name_part_0, name_part_1 = feature.split('->')
                    if isinstance(val, str): val = f"\\'{val}\\'"
                    command.update({f"command{add_index}": f"{name_part_0}:execute(0, 'setVar(\\'{name_part_1}\\', {val})')"})
                else:
                    if isinstance(val, str): val = f"\'{val}\'"
                    command.update({f"command{add_index}": f"setVar('{feature}', {val})"})

        if not command:
            return

        async with aiohttp.ClientSession() as session:
            try:
                _LOGGER.info("Prepared commands: %s", command)
                await session.post(api_endpoint, json=command)
            except Exception as e:
                _LOGGER.error("Failed to send update: %s", e)

    remove_listener = async_track_state_change_event(hass, entity_ids, state_changed)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = remove_listener

    _LOGGER.info("Grenton Watcher started for mappings: %s", mappings)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    remove_listener = hass.data[DOMAIN].pop(entry.entry_id, None)
    if remove_listener:
        remove_listener()
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
