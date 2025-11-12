"""
Visitor Analytics Tracker
Tracks visitor information including device type, bot detection, and geolocation
"""
import json
from pathlib import Path
from datetime import datetime
import re
import requests
from functools import lru_cache


class AnalyticsTracker:
    """Track visitor analytics to JSON file."""

    def __init__(self, data_file="visitor_analytics.json"):
        self.data_file = Path(data_file)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create analytics file if it doesn't exist."""
        if not self.data_file.exists():
            self.data_file.write_text(json.dumps({
                "visits": [],
                "stats": {
                    "desktop": 0,
                    "mobile": 0,
                    "tablet": 0,
                    "bot": 0,
                    "total": 0
                }
            }, indent=2))

    def detect_device_type(self, user_agent):
        """Detect device type from user agent string."""
        if not user_agent:
            return "desktop"

        user_agent = user_agent.lower()

        # Check for bots first
        if self.is_bot(user_agent):
            return "bot"

        # Check for mobile
        if any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone']):
            return "mobile"

        # Check for tablet
        if any(tablet in user_agent for tablet in ['ipad', 'tablet', 'kindle']):
            return "tablet"

        return "desktop"

    def is_bot(self, user_agent):
        """Check if user agent is a bot."""
        if not user_agent:
            return False

        bot_patterns = [
            'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget',
            'python-requests', 'gptbot', 'anthropic', 'claude',
            'googlebot', 'bingbot', 'slurp', 'duckduckbot',
            'perplexitybot', 'chatgpt'
        ]

        return any(pattern in user_agent.lower() for pattern in bot_patterns)

    def detect_bot_type(self, user_agent):
        """Detect the type of bot from user agent."""
        if not user_agent:
            return "unknown"

        user_agent = user_agent.lower()

        # AI Training bots
        training_bots = ['gptbot', 'anthropic-ai', 'claude-web', 'ccbot', 'google-extended', 'facebookbot']
        if any(bot in user_agent for bot in training_bots):
            return "training"

        # AI Search bots
        search_bots = ['chatgpt-user', 'claudebot', 'perplexitybot', 'youbot']
        if any(bot in user_agent for bot in search_bots):
            return "search"

        # Traditional search bots
        traditional_bots = ['googlebot', 'bingbot', 'slurp', 'duckduckbot', 'yandex', 'baidu']
        if any(bot in user_agent for bot in traditional_bots):
            return "traditional"

        return "unknown"

    @lru_cache(maxsize=1000)
    def get_geolocation(self, ip_address):
        """Get geolocation data from IP address using ip-api.com (free service)."""
        # Skip local/private IPs
        if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
            return None

        # Skip private IP ranges
        if ip_address.startswith(('10.', '172.', '192.168.', 'fe80:', 'fc00:', 'fd00:')):
            return None

        try:
            # Use ip-api.com free API (no key required, 45 requests/minute limit)
            response = requests.get(
                f'http://ip-api.com/json/{ip_address}',
                timeout=2  # Short timeout to avoid slowing down requests
            )

            if response.status_code == 200:
                data = response.json()

                # Check if request was successful
                if data.get('status') == 'success':
                    return {
                        'country': data.get('country'),
                        'country_code': data.get('countryCode'),
                        'region': data.get('regionName'),
                        'city': data.get('city'),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'timezone': data.get('timezone')
                    }
        except Exception as e:
            # Silently fail - geolocation is optional
            print(f"Geolocation failed for {ip_address}: {e}")
            pass

        return None

    def track_visit(self, path, user_agent, ip_address=None):
        """Track a visitor."""
        # Skip internal Dash paths and static assets
        skip_paths = [
            '.css', '.js', '.png', '.jpg', '.ico', '.svg', '.woff', '.woff2', '.ttf', '.eot',
            '_dash', '_reload-hash', 'favicon', '/_dash-update-component',
            '/_dash-layout', '/_dash-dependencies', '/_dash-component-suites',
            '/assets/', '[]'  # Also skip malformed paths
        ]
        if any(skip in path for skip in skip_paths):
            return

        # Only track valid paths that start with /
        if not path or not path.startswith('/') or path.startswith('//'):
            return

        device_type = self.detect_device_type(user_agent)

        visit_data = {
            "timestamp": datetime.now().isoformat(),
            "path": path,
            "device_type": device_type,
            "user_agent": user_agent or "Unknown",
        }

        # Add bot type if it's a bot
        if device_type == "bot":
            visit_data["bot_type"] = self.detect_bot_type(user_agent)

        if ip_address:
            visit_data["ip_address"] = ip_address

            # Try to get geolocation
            geo_data = self.get_geolocation(ip_address)
            if geo_data:
                visit_data["location"] = geo_data

        # Load existing data
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
        except:
            data = {"visits": [], "stats": {"desktop": 0, "mobile": 0, "tablet": 0, "bot": 0, "total": 0}}

        # Add visit
        data["visits"].append(visit_data)

        # Update stats
        data["stats"][device_type] = data["stats"].get(device_type, 0) + 1
        data["stats"]["total"] = data["stats"].get("total", 0) + 1

        # Save data
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)


# Global tracker instance
tracker = AnalyticsTracker()
