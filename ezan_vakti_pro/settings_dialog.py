import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class SettingsDialog(Adw.PreferencesWindow):
    def __init__(self, parent_window, storage_manager, sound_player, prayer_engine, on_settings_changed=None):
        super().__init__()
        self.set_transient_for(parent_window)
        self.set_modal(True)
        self.set_title("Ezan Vakti Pro Ayarları")
        self.set_default_size(520, 520)
        self.set_search_enabled(False)

        self.storage = storage_manager
        self.sound = sound_player
        self.engine = prayer_engine
        self.on_changed = on_settings_changed

        # =====================================================================
        # SAYFA 1: VAKİT ÖNCESİ UYARILAR (Görsel 1 Üst Kısım)
        # =====================================================================
        page_pre = Adw.PreferencesPage()
        page_pre.set_title("Vakit Öncesi")
        page_pre.set_icon_name("alarm-symbolic")
        self.add(page_pre)

        grp_pre = Adw.PreferencesGroup()
        grp_pre.set_title("Vakitlerden Önce Uyarılar")
        grp_pre.set_description("Vakit girmeden önce erken hazırlık bildirimi ve hatırlatma sesi")
        page_pre.add(grp_pre)

        self.spin_pre_min = Adw.SpinRow.new_with_range(5, 60, 5)
        self.spin_pre_min.set_title("Erken Uyarı Süresi (Dakika)")
        self.spin_pre_min.set_subtitle("Vakitten kaç dakika önce haber verilsin?")
        self.spin_pre_min.set_value(self.storage.config.get("pre_warning_minutes", 15))
        self.spin_pre_min.connect("notify::value", self._on_value_changed)
        grp_pre.add(self.spin_pre_min)

        self.sw_pre_imsak = self._create_switch_row("İmsaktan Önce", "Melodi 1", "imsak", is_pre=True)
        grp_pre.add(self.sw_pre_imsak)

        self.sw_pre_gunes = self._create_switch_row("Güneşten Önce", "Masa Saati / Melodi", "gunes", is_pre=True)
        grp_pre.add(self.sw_pre_gunes)

        self.sw_pre_ogle = self._create_switch_row("Öğleden Önce", "Melodi 1", "ogle", is_pre=True)
        grp_pre.add(self.sw_pre_ogle)

        self.sw_pre_ikindi = self._create_switch_row("İkindiden Önce", "Melodi 1", "ikindi", is_pre=True)
        grp_pre.add(self.sw_pre_ikindi)

        self.sw_pre_aksam = self._create_switch_row("Akşamdan Önce", "Melodi 1", "aksam", is_pre=True)
        grp_pre.add(self.sw_pre_aksam)

        self.sw_pre_yatsi = self._create_switch_row("Yatsıdan Önce", "Melodi 1", "yatsi", is_pre=True)
        grp_pre.add(self.sw_pre_yatsi)

        test_pre_row = Adw.ActionRow()
        test_pre_row.set_title("Ön Uyarı Tonunu Test Et")
        btn_pre_sound = Gtk.Button(label="Sesi Dinle")
        btn_pre_sound.set_valign(Gtk.Align.CENTER)
        btn_pre_sound.add_css_class("flat")
        btn_pre_sound.connect("clicked", lambda b: self.sound.play_pre_warning())
        test_pre_row.add_suffix(btn_pre_sound)
        grp_pre.add(test_pre_row)

        # =====================================================================
        # SAYFA 2: VAKİT ZAMANINDA UYARILAR & EZAN (Görsel 1 Alt Kısım)
        # =====================================================================
        page_time = Adw.PreferencesPage()
        page_time.set_title("Vakit Ezanları")
        page_time.set_icon_name("audio-volume-high-symbolic")
        self.add(page_time)

        grp_time = Adw.PreferencesGroup()
        grp_time.set_title("Vakit Zamanında Uyarılar")
        grp_time.set_description("Vakit girdiğinde ezan sesi ve masaüstü bildirimi")
        page_time.add(grp_time)

        self.sw_sound = Adw.SwitchRow()
        self.sw_sound.set_title("Sesli Uyarılar Açık")
        self.sw_sound.set_subtitle("Ezan sesleri ve bildirim melodileri çalsın")
        self.sw_sound.set_active(self.storage.config.get("sound_enabled", True))
        self.sw_sound.connect("notify::active", self._on_value_changed)
        grp_time.add(self.sw_sound)

        self.sw_time_imsak = self._create_switch_row("Sabah Ezanı", "Esselatu Hayrun / Ezan", "imsak", is_pre=False)
        grp_time.add(self.sw_time_imsak)

        self.sw_time_gunes = self._create_switch_row("Güneş Doğuşu", "Hafif Uyarı Tonu", "gunes", is_pre=False)
        grp_time.add(self.sw_time_gunes)

        self.sw_time_ogle = self._create_switch_row("Öğle Ezanı", "Ezan ve Bildirim", "ogle", is_pre=False)
        grp_time.add(self.sw_time_ogle)

        self.sw_time_ikindi = self._create_switch_row("İkindi Ezanı", "Ezan ve Bildirim", "ikindi", is_pre=False)
        grp_time.add(self.sw_time_ikindi)

        self.sw_time_aksam = self._create_switch_row("Akşam Ezanı", "Ezan ve Bildirim", "aksam", is_pre=False)
        grp_time.add(self.sw_time_aksam)

        self.sw_time_yatsi = self._create_switch_row("Yatsı Ezanı", "Ezan ve Bildirim", "yatsi", is_pre=False)
        grp_time.add(self.sw_time_yatsi)

        test_time_row = Adw.ActionRow()
        test_time_row.set_title("Ezan Sesini Test Et")
        btn_time_sound = Gtk.Button(label="Ezan Sesi Dinle")
        btn_time_sound.set_valign(Gtk.Align.CENTER)
        btn_time_sound.add_css_class("suggested-action")
        btn_time_sound.connect("clicked", lambda b: self.sound.play_ezan())
        test_time_row.add_suffix(btn_time_sound)
        grp_time.add(test_time_row)

        # =====================================================================
        # SAYFA 3: GÖRÜNÜM & PANEL KONUMU (Görsel 2 + Panel Yerleşimi)
        # =====================================================================
        page_general = Adw.PreferencesPage()
        page_general.set_title("Görünüm ve Panel")
        page_general.set_icon_name("preferences-desktop-display-symbolic")
        self.add(page_general)

        # 1. Üst Panel Konumu (GNOME Extension)
        grp_panel = Adw.PreferencesGroup()
        grp_panel.set_title("Üst Panel (GNOME Extension) Konumu")
        grp_panel.set_description("Ezan Vakti göstergesinin GNOME üst barındaki yerleşimi")
        page_general.add(grp_panel)

        self.combo_panel_pos = Adw.ComboRow()
        self.combo_panel_pos.set_title("Panel Yerleşimi")
        self.combo_panel_pos.set_subtitle("Sağ (Durum simgeleri yanı), Orta (Saat yanı) veya Sol")
        pos_model = Gtk.StringList.new(["Sağ Taraf (Right)", "Orta Kısım (Center)", "Sol Taraf (Left)"])
        self.combo_panel_pos.set_model(pos_model)

        cur_pos = self.storage.config.get("panel_position", "right")
        pos_idx = 0 if cur_pos == "right" else (1 if cur_pos == "center" else 2)
        self.combo_panel_pos.set_selected(pos_idx)
        self.combo_panel_pos.connect("notify::selected", self._on_panel_pos_changed)
        grp_panel.add(self.combo_panel_pos)

        # 2. Gece Modu (Görsel 2)
        grp_theme = Adw.PreferencesGroup()
        grp_theme.set_title("Gece Modu")
        page_general.add(grp_theme)

        self.combo_theme = Adw.ComboRow()
        self.combo_theme.set_title("Renk Teması")
        self.combo_theme.set_subtitle("Uygulama arayüz teması")
        theme_model = Gtk.StringList.new(["Sistem", "Gece Modu (Koyu)", "Gündüz Modu (Açık)"])
        self.combo_theme.set_model(theme_model)

        cur_theme = self.storage.config.get("theme_mode", "dark")
        theme_idx = 1 if cur_theme == "dark" else (2 if cur_theme == "light" else 0)
        self.combo_theme.set_selected(theme_idx)
        self.combo_theme.connect("notify::selected", self._on_theme_changed)
        grp_theme.add(self.combo_theme)

        # 3. Arka Plan & Sistem
        grp_sys = Adw.PreferencesGroup()
        grp_sys.set_title("Sistem ve Akış")
        page_general.add(grp_sys)

        self.sw_bg = Adw.SwitchRow()
        self.sw_bg.set_title("Arka Planda Çalışmaya Devam Et")
        self.sw_bg.set_subtitle("Pencere kapatıldığında üst barda çalışmaya devam eder")
        self.sw_bg.set_active(self.storage.config.get("run_in_background", True))
        self.sw_bg.connect("notify::active", self._on_value_changed)
        grp_sys.add(self.sw_bg)

        # Vakitleri Güncelle
        up_row = Adw.ActionRow()
        up_row.set_title("Vakitleri Şimdi Güncelle")
        up_row.set_subtitle("Diyanet takviminden güncel 30 günlük veriyi tazeler")
        btn_refresh = Gtk.Button(label="Güncelle")
        btn_refresh.set_valign(Gtk.Align.CENTER)
        btn_refresh.connect("clicked", self._on_refresh_clicked)
        up_row.add_suffix(btn_refresh)
        grp_sys.add(up_row)

    def _create_switch_row(self, title, subtitle, prayer_key, is_pre=True):
        row = Adw.SwitchRow()
        row.set_title(title)
        row.set_subtitle(subtitle)

        cfg_dict = self.storage.config.get("pre_warnings" if is_pre else "time_warnings", {})
        row.set_active(cfg_dict.get(prayer_key, True))
        row.connect("notify::active", self._on_value_changed)
        row._prayer_key = prayer_key
        row._is_pre = is_pre
        return row

    def _on_value_changed(self, widget, pspec):
        cfg = self.storage.config
        cfg["pre_warning_minutes"] = int(self.spin_pre_min.get_value())
        cfg["sound_enabled"] = bool(self.sw_sound.get_active())
        cfg["run_in_background"] = bool(self.sw_bg.get_active())

        # Collect prayer switches
        pre_dict = cfg.setdefault("pre_warnings", {})
        pre_dict["imsak"] = self.sw_pre_imsak.get_active()
        pre_dict["gunes"] = self.sw_pre_gunes.get_active()
        pre_dict["ogle"] = self.sw_pre_ogle.get_active()
        pre_dict["ikindi"] = self.sw_pre_ikindi.get_active()
        pre_dict["aksam"] = self.sw_pre_aksam.get_active()
        pre_dict["yatsi"] = self.sw_pre_yatsi.get_active()

        time_dict = cfg.setdefault("time_warnings", {})
        time_dict["imsak"] = self.sw_time_imsak.get_active()
        time_dict["gunes"] = self.sw_time_gunes.get_active()
        time_dict["ogle"] = self.sw_time_ogle.get_active()
        time_dict["ikindi"] = self.sw_time_ikindi.get_active()
        time_dict["aksam"] = self.sw_time_aksam.get_active()
        time_dict["yatsi"] = self.sw_time_yatsi.get_active()

        self.storage.save_config()
        if self.on_changed:
            self.on_changed()

    def _on_panel_pos_changed(self, widget, pspec):
        idx = self.combo_panel_pos.get_selected()
        pos_keys = ["right", "center", "left"]
        chosen = pos_keys[idx]
        self.storage.config["panel_position"] = chosen
        self.storage.save_config()

        parent = self.get_transient_for()
        if parent and hasattr(parent, "dbus_service") and parent.dbus_service:
            parent.dbus_service._emit_position_changed(chosen)
            parent.dbus_service.broadcast_status()

        if self.on_changed:
            self.on_changed()

    def _on_theme_changed(self, widget, pspec):
        idx = self.combo_theme.get_selected()
        theme_keys = ["system", "dark", "light"]
        chosen = theme_keys[idx]
        self.storage.config["theme_mode"] = chosen
        self.storage.save_config()

        style_mgr = Adw.StyleManager.get_default()
        if chosen == "dark":
            style_mgr.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        elif chosen == "light":
            style_mgr.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            style_mgr.set_color_scheme(Adw.ColorScheme.DEFAULT)

        if self.on_changed:
            self.on_changed()

    def _on_refresh_clicked(self, btn):
        btn.set_sensitive(False)
        self.engine.refresh_vakitler_if_needed(force=True)
        btn.set_sensitive(True)

        parent = self.get_transient_for()
        if parent and hasattr(parent, "show_toast"):
            parent.show_toast("Diyanet vakitleri başarıyla güncellendi.")
