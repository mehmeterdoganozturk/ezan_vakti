import os
import json
from datetime import datetime, date
from typing import Dict, Any, List, Optional

DEFAULT_CONFIG = {
    "country": "Türkiye",
    "country_id": "2",
    "city": "ANKARA",
    "city_id": "506",
    "district": "GÖLBAŞI",
    "district_id": "9206",
    "display_name": "Gölbaşı",
    "calculation_method": "diyanet",
    "panel_position": "right",  # "right", "center", "left"
    "theme_mode": "dark",       # "system", "dark", "light"
    "run_in_background": True,
    "pre_warning_minutes": 15,
    "pre_warnings": {
        "imsak": True,
        "gunes": False,
        "ogle": True,
        "ikindi": True,
        "aksam": True,
        "yatsi": True
    },
    "time_warnings": {
        "imsak": True,
        "gunes": False,
        "ogle": True,
        "ikindi": True,
        "aksam": True,
        "yatsi": True
    },
    "sound_enabled": True,
    "notification_enabled": True,
    "sound_pre_warning": "Melodi 1",
    "sound_time_warning": "Ezan"
}

class StorageManager:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.config/ezan-vakti-pro")
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.cache_file = os.path.join(self.config_dir, "vakitler_cache.json")

        self.config = self._load_config()
        self.vakitler_cache = self._load_cache()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cfg = DEFAULT_CONFIG.copy()
                    cfg.update(data)
                    return cfg
            except Exception as e:
                print(f"Error loading config.json: {e}")
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _load_cache(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading vakitler_cache: {e}")
        return []

    def save_cached_vakitler(self, data: List[Dict[str, Any]]):
        if not data:
            return
        self.vakitler_cache = data
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving vakitler cache: {e}")

    def get_today_vakit(self) -> Optional[Dict[str, Any]]:
        """
        Returns today's prayer times from cache, or None if not cached.
        Matches against multiple date formats (DD.MM.YYYY or YYYY-MM-DD or DD Month YYYY).
        """
        now = datetime.now()
        dot_date = now.strftime("%d.%m.%Y")
        iso_date = now.strftime("%Y-%m-%d")

        for item in self.vakitler_cache:
            kisa = item.get("MiladiTarihKisa", "")
            iso = item.get("MiladiTarihKisaIso8601", "")
            if kisa == dot_date or iso == dot_date or iso == iso_date:
                return item

        # If exact match not found, but we have items, return the first valid day or None
        if self.vakitler_cache:
            # Try to match day number
            day_str = f"{now.day:02d}."
            for item in self.vakitler_cache:
                if item.get("MiladiTarihKisa", "").startswith(day_str):
                    return item
        return None

    def get_tomorrow_vakit(self) -> Optional[Dict[str, Any]]:
        """
        Returns tomorrow's prayer times from cache (needed after Isha for next day's Imsak).
        """
        from datetime import timedelta
        tomorrow = datetime.now() + timedelta(days=1)
        dot_date = tomorrow.strftime("%d.%m.%Y")

        for item in self.vakitler_cache:
            kisa = item.get("MiladiTarihKisa", "")
            if kisa == dot_date:
                return item

        # Fallback to the next element in list after today
        today = self.get_today_vakit()
        if today and today in self.vakitler_cache:
            idx = self.vakitler_cache.index(today)
            if idx + 1 < len(self.vakitler_cache):
                return self.vakitler_cache[idx + 1]
        return None
