# Session kicker for Jellyfin
This docker image allows you to kick users out of a session after X amount of time. Built with a simple HTTP server so integration into different services & scripts should be simple.


By default Session kicker will attempt to stop media with commands & stopping encoding. If stop command not support it will delete the device, you can disable this functionality with `DELETE_DEVICE_IF_NO_MEDIA_CONTROLS`.


### or as u/llllllllillllllillll puts it
This is useful if you share your server with a bunch of knob heads who use up your monthly internet bandwidth by leaving The Simpsons playing for 12 hours straight

## Documentation
### Environment variables
- JELLYFIN_API_KEY - `Required`
	- API key for Jellyfin
- JELLYFIN_API_URL - `Required`
	- API URL for Jellyfin
- DONT_KICK_ITEM_TYPE - `Optional`
	- Default `"movie"`
	- Comma separated list of Item types what shouldn't be tracked, should be lowercase.
- MESSAGE_TIME_IN_MILLI - `Optional`
	- Default `60000`
	- Meant to be how long the message displays for, but Jellyfin doesn't respect it.
- MAX_WATCH_TIME_IN_SECONDS - `Optional`
	- Default `50.0`
	- Max watch time a user can have in seconds.
- ITEM_ID_ON_SESSION_KICKED - `Optional`
	- Default `""`
	- Item ID to play instead of stopping playback, leave blank to disable.
- WATCH_TIME_OVER_MSG - `Optional`
	- Default `"You aren't whitelisted for unlimited watch time."`
- NOT_WHITELISTED_MSG - `Optional`
	- Default `"You have used up your watch time."`
- RESET_AFTER_IN_HOURS - `Optional`
	- Default `24`
	- How many hours should the session cache be reset, set as `0` to disable.
- HTTP_HOST - `Optional`
- HTTP_PORT - `Optional`
- MONGO_DB - `Optional`
	- By default `"session_timer"`
- MONGO_HOST - `Optional`
	- By default `"localhost"`
- MONGO_PORT - `Optional`
	- By default `27017`
- DELETE_DEVICE_IF_NO_MEDIA_CONTROLS  - `Optional`
	- If device doesn't support media controls, nuke the device.
	- by default `True`
- KICK_BY_DEVICE_INSTEAD_OF_USER  - `Optional`
	- Accrue time per device rather than per user
	- by default `False`

### Deployment
- Download & configure `docker-compose.yml`
- `sudo docker-compose build; sudo docker-compose up -d`
- Proxy exposed port.

### HTTP Server
#### Authorization
- Session kicker uses [Basic Auth](https://datatracker.ietf.org/doc/html/rfc7617).
- Basic Auth credentials are display on initial run.
    - e.g. `Your basic auth: xxxx`

#### Add user to whitelist for Media type.
- Method - `POST`
- Authorization - `Basic Auth`
- Body - `Json`
##### Payload
```json
{
	"UserId": "f521b643f9914b749b9e30bbd06b1792",
	"MediaTypes": ["episode"]
}
```

#### Remove user from whitelist for Media type.
- Method - `DELETE`
- Authorization - `Basic Auth`
- Body - `Json`
##### Payload
```json
{
	"UserId": "f521b643f9914b749b9e30bbd06b1792",
	"MediaTypes": ["episode"]
}
```
#### Get all whitelisted Users.
- Method - `GET`
- Authorization - `Basic Auth`
##### Response
```json
[
	{
		"UserId": "f521b643f9914b749b9e30bbd06b1792",
		"MediaTypes": [
			"episode"
		]
	}
]
```
#### Reset HTTP Key
- Method - `PATCH`
- Authorization - `Basic Auth`

##### Response
```json
{
	"key": "d8C9ORsEzjSlUFJx8GMl8VClDmzcRLE_5B5B79Jz0QTtycw0EypqSw"
}
```
