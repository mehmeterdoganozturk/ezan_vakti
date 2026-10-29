import os
import sys
from datetime import datetime
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gdk, GLib
from .storage import StorageManager
from .diyanet_client import DiyanetClient
from .sound_player import SoundPlayer
from .notifier import DesktopNotifier
from .prayer_engine import PrayerEngine, PRAYER_KEYS, PRAYER_NAMES, PRAYER_ICONS
from .dbus_service import DBusService
from .settings_dialog import SettingsDialog
from .city_dialog import open_city_dialog

APP_ID = "com.github.erdogan.EzanVaktiPro"

class EzanApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID)
        self.window = None
        self._held = False

    def do_activate(self):
        if not self._held:
            self.hold()
            self._held = True
        if not self.window:
            self.window = EzanMainWindow(self)
        self.window.set_visible(True)
        self.window.present()

class EzanMainWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        self.storage = StorageManager()
        self.client = DiyanetClient()
        self.sound = SoundPlayer(self.storage)
        self.notifier = DesktopNotifier(self.storage)
        self.engine = PrayerEngine(self.storage, self.client, self.sound, self.notifier)

        # D-Bus IPC service for GNOME Shell Extension
        self.dbus_service = DBusService(app, self, self.engine, self.storage)

        self.set_title("Ezan Vakti Pro")
        self.set_default_size(440, 680)
        self.add_css_class("ezan-window")

        # Load custom CSS
        self._load_css()

        # Build UI layout
        self._build_ui()

        # Connect engine ticks
        self.engine.on_tick_callbacks.append(self._on_engine_tick)

        # Apply initial theme
        self._apply_theme()

        # Window close handler (keep in tray/background)
        self.connect("close-request", self._on_close_request)

    def _load_css(self):
        css_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "ezan_pro.css")
        if os.path.exists(css_file):
            provider = Gtk.CssProvider()
            provider.load_from_path(css_file)
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _apply_theme(self):
        theme_mode = self.storage.config.get("theme_mode", "dark")
        style_mgr = Adw.StyleManager.get_default()
        if theme_mode == "dark":
            style_mgr.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        elif theme_mode == "light":
            style_mgr.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            style_mgr.set_color_scheme(Adw.ColorScheme.DEFAULT)

    def _build_ui(self):
        # Toast Overlay
        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)

        # Main vertical box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.toast_overlay.set_child(main_box)

        # 1. Header Bar
        header = Adw.HeaderBar()
        header.add_css_class("ezan-header")

        # City change button on left
        self.btn_city = Gtk.Button()
        city_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        city_icon = Gtk.Image.new_from_icon_name("find-location-symbolic")
        self.lbl_header_city = Gtk.Label(label=self.storage.config.get("display_name", "Gölbaşı"))
        self.lbl_header_city.add_css_class("title-pill")
        city_box.append(city_icon)
        city_box.append(self.lbl_header_city)
        self.btn_city.set_child(city_box)
        self.btn_city.set_tooltip_text("Şehir veya İlçe Değiştir")
        self.btn_city.connect("clicked", lambda b: open_city_dialog(self, self.storage, self.client, self.engine, self._on_location_changed))
        header.pack_start(self.btn_city)

        # Title
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        title_lbl = Gtk.Label(label="🕌 Ezan Vakti Pro")
        title_lbl.add_css_class("title-pill")
        title_box.append(title_lbl)
        header.set_title_widget(title_box)

        # Refresh button
        btn_refresh = Gtk.Button(icon_name="view-refresh-symbolic")
        btn_refresh.set_tooltip_text("Vakitleri Güncelle")
        btn_refresh.connect("clicked", self._on_refresh_clicked)
        header.pack_end(btn_refresh)

        # Settings button
        btn_settings = Gtk.Button(icon_name="emblem-system-symbolic")
        btn_settings.set_tooltip_text("Ayarlar")
        btn_settings.connect("clicked", self._open_settings)
        header.pack_end(btn_settings)

        main_box.append(header)

        # Scroller container
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_vexpand(True)
        main_box.append(scroller)

        # Content box (matches user's screenshot)
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        content_box.add_css_class("ezan-main-container")
        content_box.set_halign(Gtk.Align.CENTER)
        scroller.set_child(content_box)

        # -------------------------------------------------------------
        # A. Header Location & Method Title
        # -------------------------------------------------------------
        loc_header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        loc_header.set_halign(Gtk.Align.CENTER)

        self.lbl_main_location = Gtk.Label(label=self.storage.config.get("display_name", "Gölbaşı"))
        self.lbl_main_location.add_css_class("location-title")
        loc_header.append(self.lbl_main_location)

        method_lbl = Gtk.Label(label="Diyanet Takvimi")
        method_lbl.add_css_class("location-sub")
        loc_header.append(method_lbl)
        content_box.append(loc_header)

        # -------------------------------------------------------------
        # B. Status Caption (Vaktin Çıkmasına)
        # -------------------------------------------------------------
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        status_box.set_halign(Gtk.Align.CENTER)
        self.lbl_status_caption = Gtk.Label(label="Vaktin Çıkmasına")
        self.lbl_status_caption.add_css_class("status-caption")
        status_box.append(self.lbl_status_caption)
        content_box.append(status_box)

        # -------------------------------------------------------------
        # C. Giant Countdown Clock (07:17:06)
        # -------------------------------------------------------------
        self.lbl_countdown = Gtk.Label(label="00:00:00")
        self.lbl_countdown.add_css_class("countdown-clock")
        self.lbl_countdown.set_halign(Gtk.Align.CENTER)
        content_box.append(self.lbl_countdown)

        # -------------------------------------------------------------
        # D. Date Pill Badge (Miladi & Hicri)
        # -------------------------------------------------------------
        date_pill = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        date_pill.add_css_class("date-pill-box")
        date_pill.set_halign(Gtk.Align.CENTER)

        self.lbl_date_pill = Gtk.Label(label="Yükleniyor...")
        self.lbl_date_pill.add_css_class("date-pill-text")
        date_pill.append(self.lbl_date_pill)
        content_box.append(date_pill)

        # -------------------------------------------------------------
        # E. 6 Prayer Cards Grid (2 Columns x 3 Rows)
        # -------------------------------------------------------------
        self.cards_grid = Gtk.Grid()
        self.cards_grid.set_column_spacing(14)
        self.cards_grid.set_row_spacing(12)
        self.cards_grid.set_halign(Gtk.Align.CENTER)
        content_box.append(self.cards_grid)

        self.prayer_cards = {}
        # Layout:
        # Col 0: İmsak (0,0), Öğle (0,1), Akşam (0,2)
        # Col 1: Güneş (1,0), İkindi (1,1), Yatsı (1,2)
        grid_positions = {
            "imsak": (0, 0),
            "gunes": (1, 0),
            "ogle": (0, 1),
            "ikindi": (1, 1),
            "aksam": (0, 2),
            "yatsi": (1, 2)
        }

        for p_key in PRAYER_KEYS:
            card_box, lbl_time, badge_lbl = self._create_prayer_card(p_key)
            col, row = grid_positions[p_key]
            self.cards_grid.attach(card_box, col, row, 1, 1)
            self.prayer_cards[p_key] = {
                "box": card_box,
                "lbl_time": lbl_time,
                "badge": badge_lbl
            }

        # -------------------------------------------------------------
        # F. Bottom Bar (Kıble Açısı & Hızlı Butonlar)
        # -------------------------------------------------------------
        bottom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        bottom_bar.add_css_class("bottom-bar")

        self.lbl_qibla = Gtk.Label(label="🧭 Kıble: 153° Güneydoğu | Kıble Saati: 11:25")
        self.lbl_qibla.add_css_class("qibla-badge")
        bottom_bar.append(self.lbl_qibla)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        bottom_bar.append(spacer)

        self.btn_sound_toggle = Gtk.Button()
        self.btn_sound_toggle.add_css_class("flat")
        self.btn_sound_toggle.set_tooltip_text("Sesi Aç / Kapat")
        self.btn_sound_toggle.connect("clicked", self._toggle_sound)
        bottom_bar.append(self.btn_sound_toggle)

        main_box.append(bottom_bar)

        # Trigger initial UI refresh
        self._update_sound_button()
        self._refresh_ui_with_status(self.engine.get_status())

    def _create_prayer_card(self, prayer_key: str):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        card.add_css_class("prayer-card")

        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        p_name = PRAYER_NAMES[prayer_key]
        p_icon = PRAYER_ICONS[prayer_key]

        lbl_name = Gtk.Label(label=f"{p_icon} {p_name}")
        lbl_name.add_css_class("prayer-title")
        lbl_name.set_halign(Gtk.Align.START)
        top_row.append(lbl_name)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        top_row.append(spacer)

        badge_lbl = Gtk.Label(label="")
        badge_lbl.add_css_class("prayer-badge")
        top_row.append(badge_lbl)
        card.append(top_row)

        lbl_time = Gtk.Label(label="--:--")
        lbl_time.add_css_class("prayer-time")
        lbl_time.set_halign(Gtk.Align.START)
        card.append(lbl_time)

        return card, lbl_time, badge_lbl

    def _on_engine_tick(self, status):
        GLib.idle_add(self._refresh_ui_with_status, status)

    def _refresh_ui_with_status(self, status):
        # Update countdown
        self.lbl_countdown.set_text(status["countdown_str"])

        # Update caption: "Vaktin Çıkmasına" or "Sıradaki Vakte Kalan"
        cur_name = PRAYER_NAMES.get(status["current_prayer"], "")
        next_name = status["next_prayer_name"]
        self.lbl_status_caption.set_text(f"{cur_name} Vaktinin Çıkmasına ({next_name} Vaktine)")

        # Update Date Pill
        greg = status["date_gregorian"]
        hijri = status["date_hijri"]
        self.lbl_date_pill.set_text(f"{greg} • {hijri}")

        # Update City label
        disp_name = status["district_name"]
        self.lbl_main_location.set_text(disp_name)
        self.lbl_header_city.set_text(disp_name)

        # Update Qibla
        q_time = status.get("qibla_time", "11:25")
        q_angle = status.get("qibla_angle", 153.0)
        self.lbl_qibla.set_text(f"🧭 Kıble Açısı: {q_angle}° • Kıble Saati: {q_time}")

        # Update 6 prayer cards
        today_times = status.get("today_times", {})
        cur_key = status["current_prayer"]
        next_key = status["next_prayer"]

        for p_key, c_info in self.prayer_cards.items():
            box = c_info["box"]
            lbl_time = c_info["lbl_time"]
            badge = c_info["badge"]

            time_val = today_times.get(p_key, "--:--")
            lbl_time.set_text(time_val)

            box.remove_css_class("active-prayer")
            box.remove_css_class("next-prayer")
            badge.set_text("")

            if p_key == cur_key:
                box.add_css_class("active-prayer")
                badge.set_text("● VAKİT")
            elif p_key == next_key:
                box.add_css_class("next-prayer")
                badge.set_text("▶ SIRADAKİ")

        # Update window title with countdown
        self.set_title(f"({status['countdown_str']}) {next_name} Vaktine - Ezan Vakti Pro")
        return False

    def _toggle_sound(self, btn):
        cur = self.storage.config.get("sound_enabled", True)
        self.storage.config["sound_enabled"] = not cur
        self.storage.save_config()
        self._update_sound_button()
        if self.dbus_service:
            self.dbus_service.broadcast_status()

    def _update_sound_button(self):
        is_en = self.storage.config.get("sound_enabled", True)
        self.btn_sound_toggle.set_icon_name("audio-volume-high-symbolic" if is_en else "audio-volume-muted-symbolic")

    def _open_settings(self, btn):
        dlg = SettingsDialog(
            self,
            self.storage,
            self.sound,
            self.engine,
            on_settings_changed=self._on_settings_updated
        )
        dlg.present()

    def _on_settings_updated(self):
        self._apply_theme()
        self._update_sound_button()
        self._refresh_ui_with_status(self.engine.get_status())
        if self.dbus_service:
            self.dbus_service.broadcast_status()

    def _on_location_changed(self):
        self._refresh_ui_with_status(self.engine.get_status())
        if self.dbus_service:
            self.dbus_service.broadcast_status()
        self.show_toast(f"Konum güncellendi: {self.storage.config.get('display_name')}")

    def _on_refresh_clicked(self, btn):
        btn.set_sensitive(False)
        self.engine.refresh_vakitler_if_needed(force=True)
        btn.set_sensitive(True)
        self._refresh_ui_with_status(self.engine.get_status())
        if self.dbus_service:
            self.dbus_service.broadcast_status()
        self.show_toast("Diyanet vakitleri güncellendi.")

    def show_toast(self, text: str):
        toast = Adw.Toast.new(text)
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)

    def _on_close_request(self, window):
        if self.storage.config.get("run_in_background", True):
            self.set_visible(False)
            if self.dbus_service:
                self.dbus_service.broadcast_status()
            return True
        return False
