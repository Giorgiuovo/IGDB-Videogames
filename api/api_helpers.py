import config
import requests

def get_igdb_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": config.IGDB_CLIENT_ID,
        "client_secret": config.IGDB_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()["access_token"]

HEADERS = {
    "Client-ID": config.IGDB_CLIENT_ID,
    "Authorization": f"Bearer {get_igdb_access_token()}"
}