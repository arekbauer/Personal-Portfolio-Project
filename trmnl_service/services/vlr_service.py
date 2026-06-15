import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from ..teams import TEAM_MAP

class VLRService:
    MATCHES_URL = "https://vlr.orlandomm.net/api/v1/matches"
    RESULTS_URL = "https://vlr.orlandomm.net/api/v1/results"
    WHITELIST = ["VCT 2026", "Valorant Masters", "Valorant Masters London 2026"]
    LONDON_TZ = ZoneInfo("Europe/London")
    TIME_OFFSET_HOURS = 4

    @classmethod
    def get_vct_dashboard_data(cls):
        """Main entry point: Orchestrates the data flow."""
        now = datetime.now(cls.LONDON_TZ)

        # 1. Fetch raw data
        raw_matches = cls._fetch_data(cls.MATCHES_URL)
        raw_results = cls._fetch_data(cls.RESULTS_URL, params={"page": "1"})

        # 2. Process and Filter
        # We split these so we can debug 'Matches' and 'Results' independently.
        matches = cls._process_matches(raw_matches, now)
        results = cls._process_results(raw_results, now)


        return {
            **results, # Contains y_res and t_res
            **matches, # Contains live, t_up, and tom_up
            "last_updated": now.strftime("%H:%M").lower()
        }

    # --- Private Logic: Processing ---

    @classmethod
    def _process_matches(cls, raw_data, now):
        """Handles LIVE and UPCOMING match logic."""
        buckets = {"live": [], "t_up": [], "tom_up": []}

        for item in raw_data:
            if not cls._is_whitelisted(item): continue

            match = cls._normalize_item(item)
            utc_date = item.get('utc', '')
            status = item.get('status', '').upper()

            if cls._is_date(utc_date, now): # Today
                if status == "LIVE":
                    buckets["live"].append(match)
                else:
                    buckets["t_up"].append(match)
            elif cls._is_date(utc_date, now + timedelta(days=1)): # Tomorrow
                buckets["tom_up"].append(match)

        return buckets

    @classmethod
    # TODO: Look into improving this logic due to API timezone issues
    def _process_results(cls, raw_data, now):
        """Handles COMPLETED match logic using the 'ago' field."""
        buckets = {"y_res": [], "t_res": []}

        for item in raw_data:
            if not cls._is_whitelisted(item): continue

            match = cls._normalize_item(item)
            ago_str = item.get('ago', '') # Results use 'ago' instead of 'utc'

            if 'd' not in ago_str: # Happened today
                buckets["t_res"].append(match)
            elif '1d' in ago_str: # Happened yesterday
                buckets["y_res"].append(match)

        return buckets

    # --- Private Logic: Helpers (The "Readable" Part) ---

    @staticmethod
    def _fetch_data(url, params=None):
        """Simple wrapper for requests to handle the API wrapper key."""
        try:
            resp = requests.get(url, params=params, timeout=10)
            return resp.json().get('data', [])
        except Exception:
            return []

    @staticmethod
    def _is_whitelisted(item):
        """Centralized check for your tournament whitelist."""
        tournament = item.get('tournament', '')
        return any(w in tournament for w in VLRService.WHITELIST)

    @staticmethod
    def _is_date(utc_string, target_dt):
        """Check if the API's UTC string matches our target date string."""
        return target_dt.strftime('%Y-%m-%d') in utc_string

    @staticmethod
    def _normalize_item(data):
        """Turns messy API objects into clean, display-ready dictionaries."""
        ts = data.get('timestamp')
        time_str = ""

        if ts:
            # Apply 6-hour correction and convert to London Time
            corrected_ts = ts + (VLRService.TIME_OFFSET_HOURS * 3600)
            dt_london = datetime.fromtimestamp(corrected_ts, tz=ZoneInfo("UTC")).astimezone(VLRService.LONDON_TZ)

            # FORMAT: 12-hour time
            time_str = dt_london.strftime("%I:%M%p").lower().lstrip('0')

        t1_full = data['teams'][0]['name']
        t2_full = data['teams'][1]['name']

        # Check if abbreviation exists, otherwise use full name
        t1_display = TEAM_MAP.get(t1_full, t1_full)
        t2_display = TEAM_MAP.get(t2_full, t2_full)

        # Strip "VCT 2026:" or just "VCT 2026" and any surrounding whitespace
        raw_tournament = data.get('tournament', '')
        clean_tournament = raw_tournament.replace("VCT 2026", "").replace(":", "").strip()

        return {
            "t1": t1_display,
            "s1": data['teams'][0].get('score'),
            "t2": t2_display,
            "s2": data['teams'][1].get('score'),
            "tournament": clean_tournament,
            "event": data.get('event'),
            "status": data.get('status'),
            "time": time_str
        }
