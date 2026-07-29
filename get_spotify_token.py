import urllib.parse
import urllib.request
import json
import base64
import http.server
import socketserver
import webbrowser

def main():
    print("=== Spotify Refresh Token Generator ===")
    client_id = "fd011b6488ef4ce3a92d26500154c687"
    client_secret = "d21d8ec17d174644ba75fd79e1ebc21b"
    
    redirect_uri = "http://127.0.0.1:8888/callback"
    
    # Generate auth URL
    scope = "user-read-currently-playing user-read-recently-played"
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": client_id,
        "scope": scope,
        "redirect_uri": redirect_uri
    })
    
    print("\nOpening your browser to authorize with Spotify...")
    webbrowser.open(auth_url)
    
    # Local server to catch the redirect
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if "code" in params:
                code = params["code"][0]
                self.wfile.write(b"Success! You can close this window and look at your terminal.")
                
                # Exchange code for token
                auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
                req = urllib.request.Request("https://accounts.spotify.com/api/token", data=urllib.parse.urlencode({
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri
                }).encode(), headers={
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/x-www-form-urlencoded"
                })
                
                try:
                    with urllib.request.urlopen(req) as response:
                        data = json.loads(response.read())
                        refresh_token = data.get("refresh_token")
                        print("\n" + "="*50)
                        print("SUCCESS! Here is your Refresh Token:")
                        print(refresh_token)
                        print("="*50)
                        print("\nPress Ctrl+C to exit.")
                except Exception as e:
                    print(f"Error getting token: {e}")
            else:
                self.wfile.write(b"Failed. No code found in URL.")
            
    print("Waiting for you to log in on Spotify...")
    with socketserver.TCPServer(("", 8888), Handler) as httpd:
        httpd.handle_request() # Handle just one request

if __name__ == "__main__":
    main()
