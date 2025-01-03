# twitch-plays-wolf

## Dev setup

Uses https://docs.astral.sh/uv/

## Twitch setup

Register an app at https://dev.twitch.tv/console/apps/.  
Set the following environment variables:

- `APP_ID`
- `APP_SECRET`
- `APP_REDIRECT_URI`
- `PORT` (optional, defaults to 5000)

then run the project with

```
uv run twitch-plays-wolf
```

Open up a browser and navigate to `http://localhost:5000/login` to authenticate with Twitch.