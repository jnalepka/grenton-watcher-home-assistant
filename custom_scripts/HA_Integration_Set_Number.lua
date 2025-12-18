-- ╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
-- ║                        Author: Jan Nalepka                                                           ║
-- ║                                                                                                      ║
-- ║ Script: HA_Integration_Set_Number                                                                    ║
-- ║ Description: Send a service command for an entity in Home Assistant.                                 ║
-- ║                                                                                                      ║
-- ║ License: MIT License                                                                                 ║
-- ║ Github: https://github.com/jnalepka/homeassistant-to-grenton                                         ║
-- ║                                                                                                      ║
-- ║ Version: 1.0.0                                                                                       ║
-- ║                                                                                                      ║
-- ║ Requirements:                                                                                        ║
-- ║    Gate Http:                                                                                        ║
-- ║          1.  Gate Http NAME: "GATE_HTTP" <or change it in this script>                               ║
-- ║                                                                                                      ║
-- ║    Script parameters:                                                                                ║
-- ║          1.  ha_entity, default: "number.my_number", string                                          ║
-- ║          2.  ha_method, default: "set_value", string                                                 ║
-- ║          3.  attr_value, default: 0, number                                                          ║
-- ║                                                                                                      ║
-- ║    Http_Request virtual object:                                                                      ║
-- ║          Name: HA_Request_Set                                                                        ║
-- ║          Host: http://192.168.0.114:8123  (example)                                                  ║
-- ║          Path: /api/state (any value)                                                                ║
-- ║          Method: "POST"                                                                              ║
-- ║          RequestType: JSON                                                                           ║
-- ║          ResponseType: JSON                                                                          ║
-- ║          RequestHeaders: Authorization: Bearer <your HA token>                                       ║
-- ║                                                                                                      ║
-- ║    Available methods:                                                                                ║
-- ║          -  set_value(attr_value)                                                                    ║
-- ║                                                                                                      ║
-- ║    Examples:                                                                                         ║
-- ║          - entity="number.some_number", method="set_value", value=45                                 ║
-- ║                                                                                                      ║
-- ╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝

local ha_service, ha_entity_name = string.match(ha_entity, "([^%.]+)%.([^%.]+)")
local path = "/api/services/"..ha_service.."/"..ha_method
local reqJson = { entity_id = ha_entity }

reqJson.value = attr_value 

GATE_HTTP->HA_Request_Set->SetPath(path)
GATE_HTTP->HA_Request_Set->SetRequestBody(reqJson)
GATE_HTTP->HA_Request_Set->SendRequest()
