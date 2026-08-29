"""Create a Spotify refresh token using the Authorization Code flow.

Before running this script, add http://127.0.0.1:8888/callback to your
Spotify application's Redirect URIs in the Spotify Developer Dashboard.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = "user-read-currently-playing user-read-recently-played"


def load_env(path: Path) -> dict[str, str]:
    values = dict(os.environ)
    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    return values


class CallbackHandler(BaseHTTPRequestHandler):
    authorization_code: str | None = None
    authorization_error: str | None = None
    expected_state: str = ""
    received = threading.Event()

    def do_GET(self) -> None:  # noqa: N802 (required by BaseHTTPRequestHandler)
        query = parse_qs(urlparse(self.path).query)
        state = query.get("state", [""])[0]
        callback = type(self)

        if state != callback.expected_state:
            callback.authorization_error = "The callback state did not match. Please try again."
        elif "error" in query:
            callback.authorization_error = query["error"][0]
        else:
            callback.authorization_code = query.get("code", [None])[0]
            if not callback.authorization_code:
                callback.authorization_error = "Spotify did not return an authorization code."

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        if callback.authorization_error:
            message = "Authorization failed. You can close this window and check the terminal."
        else:
            message = "Authorization received. You can close this window and return to the terminal."
        self.wfile.write(f"<h1>{message}</h1>".encode("utf-8"))
        callback.received.set()

    def log_message(self, _format: str, *_args: object) -> None:
        """Keep the one-time authorization code out of terminal logs."""


def exchange_code(client_id: str, client_secret: str, code: str) -> dict[str, object]:
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    body = urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        }
    ).encode()
    request = Request(
        "https://accounts.spotify.com/api/token",
        data=body,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urlopen(request, timeout=20) as response:  # nosec B310: fixed Spotify endpoint
        return json.loads(response.read().decode("utf-8"))


def update_env_refresh_token(path: Path, refresh_token: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    replacement = f"SPOTIFY_REFRESH_TOKEN={refresh_token}"
    for index, line in enumerate(lines):
        if line.startswith("SPOTIFY_REFRESH_TOKEN="):
            lines[index] = replacement
            break
    else:
        lines.append(replacement)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Spotify refresh token locally.")
    parser.add_argument(
        "--write-env",
        action="store_true",
        help="Replace SPOTIFY_REFRESH_TOKEN in the project's .env file.",
    )
    args = parser.parse_args()

    env = load_env(ENV_FILE)
    client_id = env.get("SPOTIFY_CLIENT_ID")
    client_secret = env.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env first.", file=sys.stderr)
        return 1

    state = secrets.token_urlsafe(24)
    CallbackHandler.expected_state = state
    CallbackHandler.authorization_code = None
    CallbackHandler.authorization_error = None
    CallbackHandler.received.clear()

    authorization_url = "https://accounts.spotify.com/authorize?" + urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "state": state,
            "show_dialog": "true",
        }
    )

    server = ThreadingHTTPServer(("127.0.0.1", 8888), CallbackHandler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    print("Opening Spotify authorization in your browser...")
    print("If it does not open, visit this URL:\n" + authorization_url)
    webbrowser.open(authorization_url)
    thread.join()
    server.server_close()

    if CallbackHandler.authorization_error:
        print(f"Spotify authorization failed: {CallbackHandler.authorization_error}", file=sys.stderr)
        return 1

    try:
        tokens = exchange_code(client_id, client_secret, CallbackHandler.authorization_code or "")
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        print(f"Spotify token exchange failed: {detail}", file=sys.stderr)
        return 1
    except URLError as error:
        print(f"Could not reach Spotify: {error.reason}", file=sys.stderr)
        return 1

    refresh_token = tokens.get("refresh_token")
    if not isinstance(refresh_token, str):
        print("Spotify did not return a refresh token.", file=sys.stderr)
        return 1

    if args.write_env:
        update_env_refresh_token(ENV_FILE, refresh_token)
        print("Refresh token saved to .env.")
    else:
        print("\nNew Spotify refresh token:\n" + refresh_token)
        print("\nRun again with --write-env to save it to .env automatically.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
