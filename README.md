# Session kicker for Jellyfin
This docker image allows you to kick users out of a session after X amount of time. This is useful if you charge for your jellyfin server but want to allow users to watch a daily amount of content for free. Built with a simple HTTP server so integration into your payment portal should be easy.

## Documentation
### Environment variables
- JELLYFIN_API_KEY - `Required`
	- API key for Jellyfin
- JELLYFIN_API_URL - `Required`
	- API URL for Jellyfin
- MEDIA_TYPE_TIME - `Optional`
	- Default `"episode"`
	- Comma separated list of Item types, should be lowercase.
- MESSAGE_TIME_IN_MILLI - `Optional`
	- Default `60000`
	- Meant to be how long the message displays for, but Jellyfin doesn't respect it.
- MAX_WATCH_TIME_IN_SECONDS - `Optional`
	- Default `50.0`
	- Max watch time a user can have in seconds.
- ITEM_ID_ON_SESSION_KICKED - `Optional`
	- Default `""`
	- Item ID to play instead of stopping playback.
- WATCH_TIME_OVER_MSG - `Optional`
	- Default `"You aren't whitelisted for unlimited watch time."`
- NOT_WHITELISTED_MSG - `Optional`
	- Default `"You have used up your watch time."`
- RESET_AFTER_IN_HOURS - `Optional`
	- Default `24`
	- How many hours should the session cache be reset.
- HTTP_HOST - `Optional`
- HTTP_PORT - `Optional`

### Deployment
- Download & configure `docker-compose.yml`
- `sudo docker-compose build; sudo docker-compose up -d`
- Proxy exposed port.

### HTTP Server
#### Authorization
- Session kicker uses [Basic Auth](https://datatracker.ietf.org/doc/html/rfc7617).
- Basic Auth credentials are display on initial run.
    - e.g. `Your basic auth: xxxx`

#### Add user to whitelist
- Method - `POST`
- Authorization - `Basic Auth`
- Body - `Json`
##### Payload
```json
{
	"UserId": "f521b643f9914b749b9e30bbd06b1792"
}
```

#### Remove user from whitelist
- Method - `DELETE`
- Authorization - `Basic Auth`
- Body - `Json`
##### Payload
```json
{
	"UserId": "f521b643f9914b749b9e30bbd06b1792"
}
```