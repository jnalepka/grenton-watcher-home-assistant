"""
==================================================
Author: Jan Nalepka
Script version: 1.0
Date: 19.11.2025
Repository: https://github.com/jnalepka/homeassistant-to-grenton
==================================================
"""

from homeassistant import config_entries
from homeassistant.helpers import selector
import voluptuous as vol

AVAILABLE_FUNCTIONS = [
    "no_convert", 
    "convert_state_on_off_to_1_0",
    "convert_brightness_to_1_0",
    "convert_hs_color_to_hue_0_360",
    "convert_hs_color_to_sat_1_0",
    "convert_hvac_state_to_coolmaster_state_0_1",
    "convert_hvac_state_to_coolmaster_connection_status",
    "convert_hvac_state_to_coolmaster_mode",
    "convert_hvac_fan_mode_to_coolmaster_fan_speed",
    "convert_hvac_swing_mode_to_coolmaster_louver",
    ]

class GrentonWatcherOptionsFlowHandler(config_entries.OptionsFlow):
    _edit_index: int | None = None
    _new_entity_id: str | None = None
    _delete_index: int | None = None

    async def async_step_init(self, user_input=None):
        if not hasattr(self, "_working_mappings"):
            self._working_mappings = list(self.config_entry.options.get("mappings", []))

        if user_input is not None:
            action = user_input["action"]
            if action == "add":
                return await self.async_step_add_entity()
            elif action == "edit":
                self._edit_index = int(user_input["mapping_index"])
                return await self.async_step_edit()
            elif action == "delete":
                self._delete_index = int(user_input["mapping_index"])
                return await self.async_step_delete()
            elif action == "save":
                return self.async_create_entry(title="", data={"mappings": self._working_mappings})

        mapping_options = [
            {"value": str(i), "label": f"{m['name']} ({m['entity_id']}, {m['attribute']})"}
            for i, m in enumerate(self._working_mappings)
        ]

        actions = ["add"]
        if mapping_options:
            actions = ["save", "add", "edit", "delete"]

        schema_dict = {}
        if mapping_options:
            schema_dict[vol.Optional("mapping_index", default=mapping_options[0]["value"])] = selector.SelectSelector({
                "options": mapping_options,
                "mode": "dropdown",
            })

        schema_dict[vol.Required("action")] = selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=actions,
                mode="dropdown",
                translation_key="action",
            )
        )

        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema_dict))

    async def async_step_add_entity(self, user_input=None):
        if user_input is not None:
            self._new_entity_id = user_input["entity_id"]
            return await self.async_step_add_attribute()

        return self.async_show_form(
            step_id="add_entity",
            data_schema=vol.Schema({vol.Required("entity_id"): selector.EntitySelector()}),
        )

    async def async_step_add_attribute(self, user_input=None):
        if user_input is not None:
            self._working_mappings.append({
                "entity_id": self._new_entity_id,
                "attribute": user_input["attribute"],
                "name": user_input["name"],
                "function": user_input["function"],
            })
            return await self.async_step_init()

        state = self.hass.states.get(self._new_entity_id)
        attributes = list(state.attributes.keys()) if state else []
        options = ["state"] + attributes

        return self.async_show_form(
            step_id="add_attribute",
            data_schema=vol.Schema({
                vol.Required("attribute"): selector.SelectSelector({"options": options, "mode": "dropdown"}),
                vol.Required("name"): str,
                vol.Required("function"): selector.SelectSelector({
                    "options": AVAILABLE_FUNCTIONS,
                    "mode": "dropdown",
                    "translation_key": "function"
                }),
            }),
        )

    async def async_step_edit(self, user_input=None):
        mapping = self._working_mappings[self._edit_index]

        if user_input is not None:
            self._working_mappings[self._edit_index] = {
                "entity_id": user_input["entity_id"],
                "attribute": user_input["attribute"],
                "name": user_input["name"],
                "function": user_input["function"],
            }
            return await self.async_step_init()

        state = self.hass.states.get(mapping["entity_id"])
        attributes = list(state.attributes.keys()) if state else []
        options = ["state"] + attributes

        return self.async_show_form(
            step_id="edit",
            data_schema=vol.Schema({
                vol.Required("entity_id", default=mapping["entity_id"]): selector.EntitySelector(),
                vol.Required("attribute", default=mapping["attribute"]): selector.SelectSelector(
                    {"options": options, "mode": "dropdown"}
                ),
                vol.Required("name", default=mapping["name"]): str,
                vol.Required("function", default=mapping.get("function", AVAILABLE_FUNCTIONS[0])): selector.SelectSelector({
                    "options": AVAILABLE_FUNCTIONS,
                    "mode": "dropdown",
                    "translation_key": "function"
                }),
            }),
        )

    async def async_step_delete(self, user_input=None):
        if self._delete_index is not None and 0 <= self._delete_index < len(self._working_mappings):
            del self._working_mappings[self._delete_index]
            return await self.async_step_init()

        return self.async_abort(reason="invalid_mapping_index")
