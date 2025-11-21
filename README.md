<img src="https://github.com/user-attachments/assets/1f08b4ab-6e7c-447a-8a26-b582f8b7157f" width="600"/>

# Grenton Watcher (Home Assistant)


Run services and read entities from Home Assistant in the Grenton system.

<a href="https://tipply.pl/@jnalepka">
    <img src="https://img.shields.io/static/v1?label=Donate&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86" alt="Donate" width="130" height="30">
</a>

<br> Watch the video how to use this integration: https://www.youtube.com/watch?v=7vgE-qqPxfQ

## Home Assistant Long-lived access token

In Home Assistant go to the Profile->Security->Long-lived access tokens, and create the long-lived access token. Token will be valid for 10 years from creation.

# Read entities from Home Assistant

1. On the Gate HTTP, create an `HttpRequest` virtual object:

   ![image](https://github.com/user-attachments/assets/dfa7284b-c2d7-409c-9e85-8979bc95d209)

   * `Name`: HA_Request_Get_States
   * `Host`: http://<your HA IP Address>:8123 (e.g. http://192.168.0.114:8123)
   * `Path`: /api/states
   * `Method`: GET
   * `RequestType`: JSON
   * `ResponseType`: JSON
   * `RequestHeadres`: Authorization: Bearer <your Long-lived access token> (e.g. Authorization: Bearer eyJhbGciOiJIUz.....)
  
2. On the Gate HTTP, create a script, named `HA_Integration_Response`:

    ```lua
    -- ╔═══════════════════════════════════════════════════════════════════════╗
    -- ║                        Author: Jan Nalepka                            ║
    -- ║                                                                       ║
    -- ║ Script: HA_Integration_Response                                       ║
    -- ║ Description: Analyze all entities from Home Assistant.                ║
    -- ║                                                                       ║
    -- ║ License: MIT License                                                  ║
    -- ║ Github: https://github.com/jnalepka/homeassistant-to-grenton          ║
    -- ║                                                                       ║
    -- ║ Version: 1.0.0                                                        ║
    -- ║                                                                       ║
    -- ║ Requirements:                                                         ║
    -- ║    Gate Http:                                                         ║
    -- ║          1.  Gate Http NAME: "GATE_HTTP" <or change it in this script>║
    -- ║                                                                       ║
    -- ║    Http_Request virtual object:                                       ║
    -- ║          Name: HA_Request_Get_States                                  ║
    -- ║          Host: http://192.168.0.114:8123  (example)                   ║
    -- ║          Path: /api/states                                            ║
    -- ║          RequestType: JSON                                            ║
    -- ║          ResponseType: JSON                                           ║
    -- ║          RequestHeaders: Authorization: Bearer <your HA token>        ║
    -- ║                                                                       ║
    -- ╚═══════════════════════════════════════════════════════════════════════╝
    
    local respJson = GATE_HTTP->HA_Request_Get_States->ResponseBody
    
    if respJson ~= nil then
    	for i = 1, #respJson do
    	    local entity_id = respJson[i].entity_id
    	    
    -- ╔═══════════════════════════════════════════════════════════════════════╗
    -- ║                   READ YOUR ENTITIES BELOW                            ║
    -- ╚═══════════════════════════════════════════════════════════════════════╝
    		
    		-- EXAMPLE, YOU CAN DELETE IT
    	
    	    if entity_id == "light.tv_light" then
    	    	if respJson[i].state == "on" then
    	    		GATE_HTTP->HA_tv_light_value = 1 -- User feature on the GATE_HTTP. Save the lamp value, i.e. to show it in the myGrenton.
    	    	else
    	    		GATE_HTTP->HA_tv_light_value = 0
    	    	end
    	    end

          if entity_id == "light.night_lamp" then
    	    	if respJson[i].state == "on" then
    	    		GATE_HTTP->HA_night_lamp_value = 1
    	    	else
    	    		GATE_HTTP->HA_night_lamp_value = 0
    	    	end
             -- example of getting an attributes
    			local FriendlyName = respJson[i].attributes.friendly_name
    			local ColorMode = respJson[i].attributes.color_mode
    	    end
    	    
    		-- END OF EXAMPLE
    	    
    		-- TO DO. Create your own conditions based on the example.
    	    
    	end
    end
    
    ```

   > Note: If you use a different name for the Gate HTTP or the virtual object, modify it in the script.

3. Attach the script to the `HA_Request_Get_States` OnResponse event:

   ![image](https://github.com/user-attachments/assets/23921008-6963-4f0c-964b-4337c9821a3f)

4. On the Gate HTTP, create a `Timer` virtual object:

   ![image](https://github.com/user-attachments/assets/4a398e02-8c5d-4246-85fa-335cd73fcbce)

   * `Name`: HA_Request_Timer
   * `Time`: 10000 ms ((You can change it if you want, but 10 seconds is quite enough)
   * `Mode`: Interval

5. Attach the `HA_Request_Get_States` SendRequest() method to the `HA_Request_Timer` OnStart and OnTimer events:

   ![image](https://github.com/user-attachments/assets/e0ac09b7-13e8-4984-8e6f-f681d37cfe1d)

6. Attach the `HA_Request_Timer` Start() method to the `GATE_HTTP` OnInit event:

   ![image](https://github.com/user-attachments/assets/f847371c-3bf0-4225-a3cc-abdf6be467b1)

# Run the Home Assistant service

1. On the Gate HTTP, create an `HttpRequest` virtual object:

   ![image](https://github.com/user-attachments/assets/2de2248c-6992-42a3-b91e-ad0506311d89)

   * `Name`: HA_Request_Set
   * `Host`: http://<your HA IP Address>:8123 (e.g. http://192.168.0.114:8123)
   * `Path`: /api/state (any value)
   * `Method`: POST
   * `RequestType`: JSON
   * `ResponseType`: JSON
   * `RequestHeadres`: Authorization: Bearer <your Long-lived access token> (e.g. Authorization: Bearer eyJhbGciOiJIUz.....)

2. On the Gate HTTP, create a script, named `HA_Integration_Set`:

    ```lua
      -- ╔═══════════════════════════════════════════════════════════════════════╗
      -- ║                        Author: Jan Nalepka                            ║
      -- ║                                                                       ║
      -- ║ Script: HA_Integration_Set                                            ║
      -- ║ Description: Send a service command for an entity in Home Assistant.  ║
      -- ║                                                                       ║
      -- ║ License: MIT License                                                  ║
      -- ║ Github: https://github.com/jnalepka/homeassistant-to-grenton          ║
      -- ║                                                                       ║
      -- ║ Version: 1.0.0                                                        ║
      -- ║                                                                       ║
      -- ║ Requirements:                                                         ║
      -- ║    Gate Http:                                                         ║
      -- ║          1.  Gate Http NAME: "GATE_HTTP" <or change it in this script>║
      -- ║                                                                       ║
      -- ║    Script parameters:                                                 ║
      -- ║          1.  ha_entity, default: "light.my_lamp", string              ║
      -- ║          2.  ha_method, default: "toggle", string                     ║
      -- ║                                                                       ║
      -- ║    Http_Request virtual object:                                       ║
      -- ║          Name: HA_Request_Set                                         ║
      -- ║          Host: http://192.168.0.114:8123  (example)                   ║
      -- ║          Path: /api/state (any value)                                 ║
      -- ║          Method: "POST"                                               ║
      -- ║          RequestType: JSON                                            ║
      -- ║          ResponseType: JSON                                           ║
      -- ║          RequestHeaders: Authorization: Bearer <your HA token>        ║
      -- ║                                                                       ║
      -- ╚═══════════════════════════════════════════════════════════════════════╝
      
      local ha_service, ha_entity_name = string.match(ha_entity, "([^%.]+)%.([^%.]+)")
      local path = "/api/services/"..ha_service.."/"..ha_method
      local reqJson = { entity_id = ha_entity }
      
      GATE_HTTP->HA_Request_Set->SetPath(path)
      GATE_HTTP->HA_Request_Set->SetRequestBody(reqJson)
      GATE_HTTP->HA_Request_Set->SendRequest()

    ```

    > Note: If you use a different name for the Gate HTTP or the virtual object, modify it in the script.

3. Add the script parameters to the `HA_Integration_Set` script:

   ![image](https://github.com/user-attachments/assets/d8e08f3d-7d67-4b77-9d2f-b5a50c7d52d9)

   * `Name`: ha_entity `Type`: string
   * `Name`: ha_method `Type`: string

4. (Optional) Attach the `HA_Request_Timer` Start() method to the `HA_Request_Set` OnResponse event:

   ![image](https://github.com/user-attachments/assets/bb1b97ed-0c33-4530-8390-06ff0992ad0d)

   This operation will update all states from HomeAssistant after the action.

5. Now you can call the `HA_Integration_Set` script from everywhere in the Grenton System!

   ![image](https://github.com/user-attachments/assets/948074ff-c0ac-4ecd-bdfa-75c5f8e74b5c)


## Simple Home Assistant services

   | ha_entity    | ha_method  | description |
   |-------------|-------------|-------------|
   | light.your_lamp | turn_on | Turn on one or more lights. |
   | light.your_lamp | turn_off | Turn off one or more lights. |
   | light.your_lamp | toggle | Toggles one or more lights, from on to off, or, off to on, based on their current state. |
   | cover.your_blinds | open_cover | Opens blinds. |
   | cover.your_blinds | close_cover | Closes blinds. |
   | cover.your_blinds | stop_cover | Stops the cover movement. |
   | cover.your_blinds | toggle | Toggles a cover open/closed. |
   | cover.your_blinds | open_cover_tilt | Tilts a cover open. |
   | cover.your_blinds | close_cover_tilt | Tilts a cover to close. |
   | cover.your_blinds | stop_cover_tilt | Stops a tilting cover movement. |
   | script.your_script | turn_on | Runs the sequence of actions defined in a script. |
   | script.your_script | turn_off | Stops a running script. |
   | script.your_script | toggle | Toggle a script. Starts it, if isn't running, stops it otherwise. |
   | switch.your_switch | turn_on | Turns a switch on. |
   | switch.your_switch | turn_off | Turns a switch off. |
   | switch.your_switch | toggle | Toggles a switch on/off. |
   | climate.your_thermostat | turn_on | Turns climate device on. |
   | climate.your_thermostat | turn_off | Turns climate device off. |
   | climate.your_thermostat | toggle | Toggles climate device, from on to off, or off to on. |

# (Optional) Use custom script to run the Home Assistant service with attributes

### For example, we will use a script located in the custom_scripts/HA_Integration_Set_Light.lua folder

   1. On the Gate HTTP, create a script, named `HA_Integration_Set_Light`:

      ```lua
        -- ╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
        -- ║                        Author: Jan Nalepka                                                           ║
        -- ║                                                                                                      ║
        -- ║ Script: HA_Integration_Set_Light                                                                     ║
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
        -- ║          1.  ha_entity, default: "light.my_lamp", string                                             ║
        -- ║          2.  ha_method, default: "toggle", string                                                    ║
        -- ║          3.  attr_brightness, default: -1, number [0-255]                                            ║
        -- ║          4.  attr_hs_color, default: "-", string "[hue, sat]", "[300, 70]"                           ║
        -- ║          5.  attr_color_temp, default: -1, number [153-500]                                          ║
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
        -- ║          -  turn_on                                                                                  ║
        -- ║          -  turn_on(attr_brightness)                                                                 ║
        -- ║          -  turn_on(attr_brightness, attr_hs_color)                                                  ║
        -- ║          -  turn_on(attr_brightness, attr_hs_color)                                                  ║
        -- ║          -  turn_off                                                                                 ║
        -- ║          -  toggle                                                                                   ║
        -- ║                                                                                                      ║
        -- ║    Examples:                                                                                         ║
        -- ║          - entity="light.lamp1", method="turn_on"                                                    ║
        -- ║          - entity="light.lamp1", method="turn_on", brightness=255                                    ║
        -- ║          - entity="light.lamp1", method="turn_on", brightness=255, hs_color="[300, 70]"              ║
        -- ║          - entity="light.lamp1", method="turn_on", brightness=255, color_temp=450                    ║
        -- ║                                                                                                      ║
        -- ╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
        
        local ha_service, ha_entity_name = string.match(ha_entity, "([^%.]+)%.([^%.]+)")
        local path = "/api/services/"..ha_service.."/"..ha_method
        local reqJson = { entity_id = ha_entity }
        
        if attr_brightness ~= -1 then 
        	reqJson.brightness = attr_brightness 
        end
        
        if attr_hs_color ~= "-" then 
        	reqJson.hs_color = attr_hs_color
        end
        
        if attr_color_temp ~= -1 then 
        	reqJson.color_temp = attr_color_temp 
        end
        
        GATE_HTTP->HA_Request_Set->SetPath(path)
        GATE_HTTP->HA_Request_Set->SetRequestBody(reqJson)
        GATE_HTTP->HA_Request_Set->SendRequest()
      ```

      > Note: If you use a different name for the Gate HTTP or the virtual object, modify it in the script.

2. Add the script parameters to the `HA_Integration_Set_Light` script:

   ![image](https://github.com/user-attachments/assets/3e2c6cfc-78a7-4fbe-a50d-8c3e1d2b30b5)

   * `Name`: ha_entity `Type`: string
   * `Name`: ha_method `Type`: string
   * `Name`: attr_brightness `Type`: number `Default`: -1  (range: 0-255)
   * `Name`: attr_hs_color `Type`: string `Default`: "-"  (example: "[300,70]", where 300 - hue in range 0-360, 70 is saturation in range 0-100)
   * `Name`: attr_color_temp `Type`: number `Default`: -1  (range: 153-500), where 153 is cold≈6500K, 500 is warm≈2000K
  

## Examples
   
   | ha_entity    | ha_method  | attr_brightness | attr_hs_color | attr_color_temp |  description |
   |-------------|-------------|-------------|-------------|-------------|-------------|
   | light.your_lamp | turn_on | [0-255] | default | default | Turn on one or more lights and set brightness. |
   | light.your_lamp | turn_on | [0-255] | "[300,70]" | default | Turn on one or more lights and set brightness, hue and saturation. |
   | light.your_lamp | turn_on | [0-255] | default | [153-500] | Turn on one or more lights and set brightness and color temperature. |
