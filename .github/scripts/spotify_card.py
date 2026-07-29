import requests
import base64
import os
import json

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]

def get_access_token():
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }, headers={"Authorization": f"Basic {auth}"})
    return res.json().get("access_token")

def get_now_playing(token):
    res = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers={
        "Authorization": f"Bearer {token}"
    })
    if res.status_code == 200 and res.text:
        data = res.json()
        if data.get("item"):
            item = data["item"]
            return {
                "title": item["name"],
                "artist": ", ".join(a["name"] for a in item["artists"]),
                "album": item["album"]["name"],
                "url": item["external_urls"]["spotify"],
                "is_playing": data["is_playing"]
            }
    # Fallback: recently played
    res2 = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=1", headers={
        "Authorization": f"Bearer {token}"
    })
    if res2.status_code == 200:
        items = res2.json().get("items", [])
        if items:
            item = items[0]["track"]
            return {
                "title": item["name"],
                "artist": ", ".join(a["name"] for a in item["artists"]),
                "album": item["album"]["name"],
                "url": item["external_urls"]["spotify"],
                "is_playing": False
            }
    return None

def generate_svg(track):
    status = "NOW PLAYING" if track["is_playing"] else "LAST PLAYED"
    bar_anim = """
        <rect x="2" y="14" width="4" height="7" rx="1" fill="#1DB954" opacity="0.9">
            <animate attributeName="height" values="2;14;6;10;4;12;2" dur="1s" repeatCount="indefinite"/>
            <animate attributeName="y" values="19;7;15;11;17;9;19" dur="1s" repeatCount="indefinite"/>
        </rect>
        <rect x="8" y="10" width="4" height="11" rx="1" fill="#1DB954" opacity="0.7">
            <animate attributeName="height" values="10;4;14;2;12;6;10" dur="1.2s" repeatCount="indefinite"/>
            <animate attributeName="y" values="11;17;7;19;9;15;11" dur="1.2s" repeatCount="indefinite"/>
        </rect>
        <rect x="14" y="6" width="4" height="15" rx="1" fill="#1DB954" opacity="0.9">
            <animate attributeName="height" values="14;6;2;12;4;10;14" dur="0.9s" repeatCount="indefinite"/>
            <animate attributeName="y" values="7;15;19;9;17;11;7" dur="0.9s" repeatCount="indefinite"/>
        </rect>
    """ if track["is_playing"] else """
        <rect x="2" y="14" width="4" height="7" rx="1" fill="#888"/>
        <rect x="8" y="10" width="4" height="11" rx="1" fill="#888"/>
        <rect x="14" y="6" width="4" height="15" rx="1" fill="#888"/>
    """
    
    title = track["title"][:35] + ("..." if len(track["title"]) > 35 else "")
    artist = track["artist"][:40] + ("..." if len(track["artist"]) > 40 else "")

    svg = f"""<svg width="480" height="130" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0d1117"/>
      <stop offset="100%" style="stop-color:#161b22"/>
    </linearGradient>
    <clipPath id="roundedRect">
      <rect width="480" height="130" rx="16" ry="16"/>
    </clipPath>
  </defs>

  <!-- Background -->
  <rect width="480" height="130" rx="16" ry="16" fill="url(#bg)" stroke="#1DB954" stroke-width="1.5" stroke-opacity="0.5"/>

  <!-- Spotify Icon -->
  <circle cx="48" cy="65" r="24" fill="#1DB954" opacity="0.15"/>
  <text x="48" y="70" font-size="26" text-anchor="middle" font-family="Arial">&#127925;</text>

  <!-- Status label -->
  <text x="85" y="30" font-family="'Courier New', monospace" font-size="10" fill="#1DB954" font-weight="bold" letter-spacing="2">{status}</text>

  <!-- Song Title -->
  <text x="85" y="60" font-family="'Segoe UI', Arial, sans-serif" font-size="18" fill="#ffffff" font-weight="700">{title}</text>

  <!-- Artist -->
  <text x="85" y="82" font-family="'Segoe UI', Arial, sans-serif" font-size="13" fill="#8b949e">{artist}</text>

  <!-- Album -->
  <text x="85" y="100" font-family="'Segoe UI', Arial, sans-serif" font-size="11" fill="#484f58">{track["album"][:45]}</text>

  <!-- Animated Bars (bottom right) -->
  <g transform="translate(435, 108)">
    {bar_anim}
  </g>

  <!-- Green accent line -->
  <rect x="0" y="126" width="480" height="4" rx="2" fill="#1DB954" opacity="0.7"/>
</svg>"""
    return svg

def main():
    print("Fetching Spotify data...")
    token = get_access_token()
    track = get_now_playing(token)
    
    if not track:
        print("No track data available.")
        track = {"title": "Not playing right now", "artist": "—", "album": "—", "url": "#", "is_playing": False}

    print(f"Track: {track['title']} by {track['artist']}")
    
    svg = generate_svg(track)
    os.makedirs("assets", exist_ok=True)
    with open("assets/spotify-card.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("SVG card generated successfully!")

if __name__ == "__main__":
    main()
