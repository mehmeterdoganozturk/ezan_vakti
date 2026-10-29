import os
import subprocess
import threading

class DesktopNotifier:
    def __init__(self, storage_manager):
        self.storage = storage_manager
        self.icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")

    def notify_pre_prayer(self, prayer_name: str, minutes_remaining: int, prayer_time: str):
        if not self.storage.config.get("notification_enabled", True):
            return

        title = f"⏳ {prayer_name} Vaktine {minutes_remaining} Dakika Kaldı"
        message = f"Vakit Saati: {prayer_time}\nHazırlanma ve abdest vakti. Hayırlı ibadetler!"
        self._send_notification(title, message, urgency="normal")

    def notify_prayer_time(self, prayer_name: str, prayer_time: str):
        if not self.storage.config.get("notification_enabled", True):
            return

        title = f"🕌 {prayer_name} Vakti Girdi"
        message = f"Vakit Saati: {prayer_time}\nHaydi namaza, haydi kurtuluşa!"
        self._send_notification(title, message, urgency="critical")

    def _send_notification(self, title: str, message: str, urgency: str = "normal"):
        def _worker():
            try:
                cmd = [
                    "notify-send",
                    "--app-name=Ezan Vakti Pro",
                    f"--urgency={urgency}",
                    "--hint=int:transient:1"
                ]
                if os.path.exists(self.icon_path):
                    cmd.append(f"--icon={self.icon_path}")
                else:
                    cmd.append("--icon=alarm-symbolic")

                cmd.extend([title, message])
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Notification dispatch error: {e}")

        threading.Thread(target=_worker, daemon=True).start()
