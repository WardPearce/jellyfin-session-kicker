# Session kicker for Jellyfin
This docker image allows you to kick users out of a session after X amount of time. This is useful if you charge for your jellyfin server but want to allow users to watch a daily amount of content for free. Built with a simple HTTP server so integration into your payment portal should be easy.

## Documentation
### Deployment
TBD

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