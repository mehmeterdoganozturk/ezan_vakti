import json
import os
from gi.repository import Gio, GLib

BUS_NAME = "com.github.erdogan.EzanVaktiPro"
OBJECT_PATH = "/com/github/erdogan/EzanVaktiPro"
INTERFACE_NAME = "com.github.erdogan.EzanVaktiPro"

INTROSPECTION_XML = f"""
<node>
  <interface name="{INTERFACE_NAME}">
    <method name="ShowWindow"/>
    <method name="HideWindow"/>
    <method name="ToggleSound"/>
    <method name="RefreshTimes"/>
    <method name="SetPanelPosition">
      <arg type="s" name="position" direction="in"/>
    </method>
    <method name="Quit"/>
    <method name="GetStatus">
      <arg type="s" name="next_name" direction="out"/>
      <arg type="s" name="next_time" direction="out"/>
      <arg type="i" name="remaining_sec" direction="out"/>
      <arg type="s" name="countdown_str" direction="out"/>
      <arg type="s" name="current_name" direction="out"/>
      <arg type="s" name="district_name" direction="out"/>
      <arg type="s" name="panel_position" direction="out"/>
      <arg type="b" name="sound_enabled" direction="out"/>
      <arg type="b" name="window_visible" direction="out"/>
    </method>
    <method name="GetTodayTimes">
      <arg type="s" name="imsak" direction="out"/>
      <arg type="s" name="gunes" direction="out"/>
      <arg type="s" name="ogle" direction="out"/>
      <arg type="s" name="ikindi" direction="out"/>
      <arg type="s" name="aksam" direction="out"/>
      <arg type="s" name="yatsi" direction="out"/>
      <arg type="s" name="qibla_time" direction="out"/>
      <arg type="d" name="qibla_angle" direction="out"/>
      <arg type="s" name="date_hijri" direction="out"/>
    </method>
    <signal name="StatusChanged">
      <arg type="s" name="next_name"/>
      <arg type="s" name="next_time"/>
      <arg type="i" name="remaining_sec"/>
      <arg type="s" name="countdown_str"/>
      <arg type="s" name="current_name"/>
      <arg type="s" name="district_name"/>
      <arg type="s" name="panel_position"/>
      <arg type="b" name="sound_enabled"/>
      <arg type="b" name="window_visible"/>
    </signal>
    <signal name="PanelPositionChanged">
      <arg type="s" name="position"/>
    </signal>
  </interface>
</node>
"""

class DBusService:
    def __init__(self, app, window, prayer_engine, storage):
        self.app = app
        self.window = window
        self.engine = prayer_engine
        self.storage = storage

        self.connection = None
        self.registration_id = 0
        self.owner_id = 0

        self.node_info = Gio.DBusNodeInfo.new_for_xml(INTROSPECTION_XML)
        self.interface_info = self.node_info.interfaces[0]

        self.live_state_file = os.path.expanduser("~/.config/ezan-vakti-pro/live_state.json")

        self.owner_id = Gio.bus_own_name(
            Gio.BusType.SESSION,
            BUS_NAME,
            Gio.BusNameOwnerFlags.NONE,
            self._on_bus_acquired,
            self._on_name_acquired,
            self._on_name_lost
        )

        self.engine.on_tick_callbacks.append(self._on_tick)

    def _on_bus_acquired(self, connection, name):
        self.connection = connection
        self.registration_id = connection.register_object(
            OBJECT_PATH,
            self.interface_info,
            self._handle_method_call,
            None,
            None
        )

    def _on_name_acquired(self, connection, name):
        self.broadcast_status()

    def _on_name_lost(self, connection, name):
        pass

    def _handle_method_call(self, connection, sender, object_path, interface_name, method_name, parameters, invocation):
        if method_name == "ShowWindow":
            GLib.idle_add(self._do_show_window)
            invocation.return_value(None)

        elif method_name == "HideWindow":
            GLib.idle_add(self._do_hide_window)
            invocation.return_value(None)

        elif method_name == "ToggleSound":
            cur = self.storage.config.get("sound_enabled", True)
            self.storage.config["sound_enabled"] = not cur
            self.storage.save_config()
            self.broadcast_status()
            invocation.return_value(None)

        elif method_name == "RefreshTimes":
            self.engine.refresh_vakitler_if_needed(force=True)
            self.broadcast_status()
            invocation.return_value(None)

        elif method_name == "SetPanelPosition":
            pos = parameters[0]
            if hasattr(pos, "unpack"):
                pos = pos.unpack()
            while isinstance(pos, (tuple, list)) and len(pos) > 0:
                pos = pos[0]
            if isinstance(pos, str) and pos in ("left", "center", "right"):
                self.storage.config["panel_position"] = pos
                self.storage.save_config()
                self._emit_position_changed(pos)
                self.broadcast_status()
            invocation.return_value(None)

        elif method_name == "Quit":
            GLib.idle_add(self._do_quit)
            invocation.return_value(None)

        elif method_name == "GetStatus":
            status_tuple = self._get_status_tuple()
            invocation.return_value(GLib.Variant('(ssissssbb)', status_tuple))

        elif method_name == "GetTodayTimes":
            times_tuple = self._get_today_times_tuple()
            invocation.return_value(GLib.Variant('(sssssssds)', times_tuple))

        else:
            invocation.return_value(None)

    def _do_show_window(self):
        if self.window:
            self.window.set_visible(True)
            self.window.present()
        self.broadcast_status()
        return False

    def _do_hide_window(self):
        if self.window:
            self.window.set_visible(False)
        self.broadcast_status()
        return False

    def _do_quit(self):
        self._write_dead_state()
        if self.app:
            self.app.quit()
        return False

    def _get_status_tuple(self):
        st = self.engine.get_status()
        next_name = st["next_prayer_name"]
        next_time = st["next_prayer_time"]
        rem_sec = int(st["remaining_seconds"])
        countdown_str = st["countdown_str"]
        cur_name = st["current_prayer"]
        dist_name = st["district_name"]
        pos = self.storage.config.get("panel_position", "right")
        sound_en = self.storage.config.get("sound_enabled", True)
        is_vis = self.window.get_visible() if self.window else False

        return (next_name, next_time, rem_sec, countdown_str, cur_name, dist_name, pos, sound_en, is_vis)

    def _get_today_times_tuple(self):
        st = self.engine.get_status()
        tt = st.get("today_times", {})
        imsak = tt.get("imsak", "05:43")
        gunes = tt.get("gunes", "07:07")
        ogle = tt.get("ogle", "12:37")
        ikindi = tt.get("ikindi", "15:30")
        aksam = tt.get("aksam", "17:58")
        yatsi = tt.get("yatsi", "19:17")
        qibla_time = st.get("qibla_time", "11:25")
        qibla_angle = float(st.get("qibla_angle", 153.0))
        hijri = st.get("date_hijri", "Hicri")

        return (imsak, gunes, ogle, ikindi, aksam, yatsi, qibla_time, qibla_angle, hijri)

    def _on_tick(self, status):
        self.broadcast_status()

    def _sync_top_bar_organizer(self, pos: str):
        try:
            import subprocess
            roles = ["ezan-vakti", "ezan-vakti-pro"]
            for b in ["left", "center", "right"]:
                key = f"/org/gnome/shell/extensions/top-bar-organizer/{b}-box-order"
                try:
                    raw = subprocess.check_output(["dconf", "read", key], stderr=subprocess.DEVNULL).decode().strip()
                except Exception:
                    continue
                arr = eval(raw) if raw else []
                arr = [x for x in arr if x not in roles]
                if b == pos:
                    arr.insert(0, "ezan-vakti")
                    arr.insert(1, "ezan-vakti-pro")
                val = str(arr).replace('"', "'")
                subprocess.check_call(["dconf", "write", key, val], stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def _emit_position_changed(self, position: str):
        self._sync_top_bar_organizer(position)
        if self.connection and self.registration_id > 0:
            try:
                self.connection.emit_signal(
                    None,
                    OBJECT_PATH,
                    INTERFACE_NAME,
                    "PanelPositionChanged",
                    GLib.Variant('(s)', (position,))
                )
            except Exception as e:
                print(f"Error emitting PanelPositionChanged: {e}")

    def broadcast_status(self):
        status_tuple = self._get_status_tuple()
        if self.connection and self.registration_id > 0:
            try:
                self.connection.emit_signal(
                    None,
                    OBJECT_PATH,
                    INTERFACE_NAME,
                    "StatusChanged",
                    GLib.Variant('(ssissssbb)', status_tuple)
                )
            except Exception:
                pass

        try:
            next_name, next_time, rem_sec, countdown_str, cur_name, dist_name, pos, sound_en, is_vis = status_tuple
            state_data = {
                "next_name": next_name,
                "next_time": next_time,
                "remaining_seconds": rem_sec,
                "countdown_str": countdown_str,
                "current_name": cur_name,
                "district_name": dist_name,
                "panel_position": pos,
                "sound_enabled": sound_en,
                "window_visible": is_vis,
                "running": True
            }
            with open(self.live_state_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f, ensure_ascii=False)
        except Exception:
            pass

    def _write_dead_state(self):
        try:
            with open(self.live_state_file, "w", encoding="utf-8") as f:
                json.dump({"running": False}, f)
        except Exception:
            pass
