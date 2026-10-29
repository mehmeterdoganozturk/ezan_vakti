import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, date

USER_AGENT = "EzanVaktiPro/1.0.0 (Linux; Wayland; GNOME 50.1)"

class DiyanetClient:
    def __init__(self, assets_dir=None):
        if not assets_dir:
            assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self.assets_dir = assets_dir
        self.turkey_districts_file = os.path.join(self.assets_dir, "turkey_districts.json")
        self._cached_locations = None

    def load_turkey_locations(self):
        if self._cached_locations is not None:
            return self._cached_locations

        if os.path.exists(self.turkey_districts_file):
            try:
                with open(self.turkey_districts_file, "r", encoding="utf-8") as f:
                    self._cached_locations = json.load(f)
                    return self._cached_locations
            except Exception as e:
                print(f"Error loading turkey_districts: {e}")
        return {}

    def fetch_diyanet_vakitler(self, district_id: str):
        """
        Fetches 30+ days of official Diyanet prayer times from ezanvakti.emushaf.net.
        Returns list of daily dictionaries or None on failure.
        """
        url = f"https://ezanvakti.emushaf.net/vakitler/{district_id}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=7) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, list) and len(data) > 0 and "Imsak" in data[0]:
                    return data
        except Exception as e:
            print(f"Diyanet API fetch error for district {district_id}: {e}")
        return None

    def fetch_aladhan_vakitler(self, city: str, country: str = "Turkey", method: int = 13):
        """
        Fallback API: AlAdhan API (Method 13 = Diyanet İşleri Başkanlığı).
        """
        encoded_city = urllib.parse.quote(city)
        encoded_country = urllib.parse.quote(country)
        today_str = datetime.now().strftime("%d-%m-%Y")
        url = f"https://api.aladhan.com/v1/timingsByCity/{today_str}?city={encoded_city}&country={encoded_country}&method={method}"

        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=7) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("code") == 200 and "data" in result:
                    timings = result["data"]["timings"]
                    date_info = result["data"]["date"]
                    gregorian = date_info.get("gregorian", {})
                    hijri = date_info.get("hijri", {})

                    # Format similarly to Diyanet schema
                    day_item = {
                        "MiladiTarihKisa": gregorian.get("date", datetime.now().strftime("%d.%m.%Y")),
                        "MiladiTarihUzun": f"{gregorian.get('day')} {gregorian.get('month', {}).get('en')} {gregorian.get('year')}",
                        "HicriTarihUzun": f"{hijri.get('day')} {hijri.get('month', {}).get('tr', hijri.get('month', {}).get('en', 'Hicri'))} {hijri.get('year')}",
                        "Imsak": timings.get("Fajr", "05:40")[:5],
                        "Gunes": timings.get("Sunrise", "07:05")[:5],
                        "Ogle": timings.get("Dhuhr", "12:35")[:5],
                        "Ikindi": timings.get("Asr", "15:30")[:5],
                        "Aksam": timings.get("Maghrib", "17:55")[:5],
                        "Yatsi": timings.get("Isha", "19:15")[:5],
                        "KibleSaati": "11:25"
                    }
                    return [day_item]
        except Exception as e:
            print(f"AlAdhan API fallback error: {e}")
        return None

    def detect_ip_location(self):
        """
        Determines current city, coordinates and timezone via ip-api.com.
        """
        try:
            req = urllib.request.Request("http://ip-api.com/json", headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == "success":
                    return {
                        "city": data.get("city", "Ankara"),
                        "region": data.get("regionName", "Ankara"),
                        "country": data.get("country", "Türkiye"),
                        "countryCode": data.get("countryCode", "TR"),
                        "lat": data.get("lat", 39.97),
                        "lon": data.get("lon", 32.82),
                        "timezone": data.get("timezone", "Europe/Istanbul")
                    }
        except Exception as e:
            print(f"IP Geolocation detection error: {e}")
        return {
            "city": "Ankara",
            "region": "Ankara",
            "country": "Türkiye",
            "countryCode": "TR",
            "lat": 39.97,
            "lon": 32.82,
            "timezone": "Europe/Istanbul"
        }

    def search_locations(self, query: str):
        """
        Searches city & district database by query string (case-insensitive Turkish).
        Returns list of {"city_name", "city_id", "district_name", "district_id"}.
        """
        locations = self.load_turkey_locations()
        query = query.strip().upper()
        # Turkish char replacements for fuzzy matching
        q_norm = query.replace("I", "İ").replace("ı", "i")

        results = []
        for cid, cinfo in locations.items():
            city_name = cinfo.get("city_name", "")
            dists = cinfo.get("districts", [])
            for d in dists:
                dist_name = d.get("IlceAdi", "")
                dist_id = d.get("IlceID", "")

                full_str = f"{city_name} {dist_name}".upper()
                if query in full_str or q_norm in full_str:
                    results.append({
                        "city_name": city_name,
                        "city_id": cid,
                        "district_name": dist_name,
                        "district_id": dist_id,
                        "display_name": f"{city_name} / {dist_name}" if dist_name != city_name else city_name
                    })

        return results[:30]
