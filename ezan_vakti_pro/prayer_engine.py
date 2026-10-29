import math
import time
from datetime import datetime, timedelta
from gi.repository import GLib

KAABA_LAT = 21.422487
KAABA_LON = 39.826206

PRAYER_KEYS = ["imsak", "gunes", "ogle", "ikindi", "aksam", "yatsi"]

PRAYER_NAMES = {
    "imsak": "İmsak",
    "gunes": "Güneş",
    "ogle": "Öğle",
    "ikindi": "İkindi",
    "aksam": "Akşam",
    "yatsi": "Yatsı"
}

PRAYER_ICONS = {
    "imsak": "🌙",
    "gunes": "🌅",
    "ogle": "☀️",
    "ikindi": "🌤️",
    "aksam": "🌇",
    "yatsi": "🌌"
}

class PrayerEngine:
    def __init__(self, storage_manager, diyanet_client, sound_player, notifier):
        self.storage = storage_manager
        self.client = diyanet_client
        self.sound = sound_player
        self.notifier = notifier

        self.on_tick_callbacks = []
        self.on_prayer_change_callbacks = []

        self._glib_source_id = None
        self._last_alert_key = None
        self._last_pre_alert_key = None

        # Ensure cache is filled or fetch initial
        self.refresh_vakitler_if_needed()

        # Start 1-second ticker
        self._glib_source_id = GLib.timeout_add_seconds(1, self._on_tick)

    def refresh_vakitler_if_needed(self, force: bool = False):
        today = self.storage.get_today_vakit()
        if not today or force:
            dist_id = self.storage.config.get("district_id", "9206")
            times = self.client.fetch_diyanet_vakitler(dist_id)
            if times:
                self.storage.save_cached_vakitler(times)
            else:
                # Fallback to Aladhan
                city = self.storage.config.get("city", "Ankara")
                al_times = self.client.fetch_aladhan_vakitler(city)
                if al_times:
                    self.storage.save_cached_vakitler(al_times)

    def _parse_time_today(self, time_str: str, base_date: datetime = None) -> datetime:
        if base_date is None:
            base_date = datetime.now()
        h, m = map(int, time_str.split(":")[:2])
        return base_date.replace(hour=h, minute=m, second=0, microsecond=0)

    def calculate_qibla_angle(self, lat: float = 39.97, lon: float = 32.82) -> float:
        """
        Calculates Great-Circle azimuth angle towards Kaaba in degrees (0-360).
        """
        phi1 = math.radians(lat)
        phi2 = math.radians(KAABA_LAT)
        delta_lambda = math.radians(KAABA_LON - lon)

        y = math.sin(delta_lambda) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)

        bearing = math.atan2(y, x)
        degrees = (math.degrees(bearing) + 360) % 360
        return round(degrees, 1)

    def get_status(self):
        """
        Returns full state object for UI & Extension:
        - current_prayer: str (e.g. "ogle")
        - next_prayer: str (e.g. "ikindi")
        - next_prayer_name: str ("İkindi")
        - next_prayer_time: str ("15:30")
        - remaining_seconds: int
        - countdown_str: str ("07:17:06")
        - date_gregorian: str ("29 Ekim 2026")
        - date_hijri: str ("18 Cemazi-el Evvel 1448")
        - today_times: dict of 6 prayers
        - qibla_time: str ("11:25")
        - qibla_angle: float
        """
        now = datetime.now()
        today_data = self.storage.get_today_vakit()
        tomorrow_data = self.storage.get_tomorrow_vakit()

        if not today_data:
            # Emergency fallback if no internet and empty cache
            return {
                "current_prayer": "ogle",
                "next_prayer": "ikindi",
                "next_prayer_name": "İkindi",
                "next_prayer_time": "15:30",
                "remaining_seconds": 3600,
                "countdown_str": "01:00:00",
                "date_gregorian": now.strftime("%d %B %Y"),
                "date_hijri": "Hicri Takvim",
                "today_times": {"imsak": "05:43", "gunes": "07:07", "ogle": "12:37", "ikindi": "15:30", "aksam": "17:58", "yatsi": "19:17"},
                "qibla_time": "11:25",
                "qibla_angle": 153.0
            }

        # Times
        times_map = {
            "imsak": today_data.get("Imsak", "05:43"),
            "gunes": today_data.get("Gunes", "07:07"),
            "ogle": today_data.get("Ogle", "12:37"),
            "ikindi": today_data.get("Ikindi", "15:30"),
            "aksam": today_data.get("Aksam", "17:58"),
            "yatsi": today_data.get("Yatsi", "19:17")
        }

        dt_imsak = self._parse_time_today(times_map["imsak"], now)
        dt_gunes = self._parse_time_today(times_map["gunes"], now)
        dt_ogle = self._parse_time_today(times_map["ogle"], now)
        dt_ikindi = self._parse_time_today(times_map["ikindi"], now)
        dt_aksam = self._parse_time_today(times_map["aksam"], now)
        dt_yatsi = self._parse_time_today(times_map["yatsi"], now)

        # Determine current & next prayer
        if now < dt_imsak:
            cur_key = "yatsi"
            next_key = "imsak"
            target_dt = dt_imsak
        elif now < dt_gunes:
            cur_key = "imsak"
            next_key = "gunes"
            target_dt = dt_gunes
        elif now < dt_ogle:
            cur_key = "gunes"
            next_key = "ogle"
            target_dt = dt_ogle
        elif now < dt_ikindi:
            cur_key = "ogle"
            next_key = "ikindi"
            target_dt = dt_ikindi
        elif now < dt_aksam:
            cur_key = "ikindi"
            next_key = "aksam"
            target_dt = dt_aksam
        elif now < dt_yatsi:
            cur_key = "aksam"
            next_key = "yatsi"
            target_dt = dt_yatsi
        else:
            # After Yatsi: Next is tomorrow's Imsak
            cur_key = "yatsi"
            next_key = "imsak"
            if tomorrow_data:
                t_imsak_str = tomorrow_data.get("Imsak", times_map["imsak"])
                target_dt = self._parse_time_today(t_imsak_str, now + timedelta(days=1))
            else:
                target_dt = dt_imsak + timedelta(days=1)

        diff = target_dt - now
        rem_sec = max(0, int(diff.total_seconds()))

        hours = rem_sec // 3600
        mins = (rem_sec % 3600) // 60
        secs = rem_sec % 60
        countdown_str = f"{hours:02d}:{mins:02d}:{secs:02d}"

        # Dates
        greg_str = today_data.get("MiladiTarihUzun", now.strftime("%d %B %Y"))
        hijri_str = today_data.get("HicriTarihUzun", "Hicri")

        qibla_time = today_data.get("KibleSaati", "11:25")
        qibla_angle = self.calculate_qibla_angle()

        return {
            "current_prayer": cur_key,
            "next_prayer": next_key,
            "next_prayer_name": PRAYER_NAMES[next_key],
            "next_prayer_time": times_map.get(next_key, target_dt.strftime("%H:%M")),
            "remaining_seconds": rem_sec,
            "countdown_str": countdown_str,
            "date_gregorian": greg_str,
            "date_hijri": hijri_str,
            "today_times": times_map,
            "qibla_time": qibla_time,
            "qibla_angle": qibla_angle,
            "district_name": self.storage.config.get("display_name", "Gölbaşı")
        }

    def _on_tick(self) -> bool:
        status = self.get_status()
        rem_sec = status["remaining_seconds"]
        next_key = status["next_prayer"]
        next_name = status["next_prayer_name"]
        next_time = status["next_prayer_time"]

        pre_mins = self.storage.config.get("pre_warning_minutes", 15)
        pre_sec_target = pre_mins * 60

        # 1. Pre-prayer warning check (e.g. 15 min remaining)
        pre_alert_id = f"{next_key}_{datetime.now().strftime('%Y%m%d')}"
        if 0 < rem_sec <= pre_sec_target and rem_sec > (pre_sec_target - 2):
            if self._last_pre_alert_key != pre_alert_id:
                self._last_pre_alert_key = pre_alert_id
                pre_cfgs = self.storage.config.get("pre_warnings", {})
                if pre_cfgs.get(next_key, True):
                    self.sound.play_pre_warning()
                    self.notifier.notify_pre_prayer(next_name, pre_mins, next_time)

        # 2. Prayer at-time alert check
        alert_id = f"{next_key}_{next_time}_{datetime.now().strftime('%Y%m%d')}"
        if rem_sec <= 1 and self._last_alert_key != alert_id:
            self._last_alert_key = alert_id
            time_cfgs = self.storage.config.get("time_warnings", {})
            if time_cfgs.get(next_key, True):
                self.sound.play_ezan()
                self.notifier.notify_prayer_time(next_name, next_time)

            for cb in self.on_prayer_change_callbacks:
                try:
                    cb(status)
                except Exception as e:
                    print(f"Error in on_prayer_change callback: {e}")

        # 3. Notify tick callbacks
        for cb in self.on_tick_callbacks:
            try:
                cb(status)
            except Exception as e:
                print(f"Error in on_tick callback: {e}")

        return True
