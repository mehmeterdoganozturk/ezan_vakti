import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import Clutter from 'gi://Clutter';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';

const BUS_NAME = 'com.github.erdogan.EzanVaktiPro';
const OBJECT_PATH = '/com/github/erdogan/EzanVaktiPro';

const EzanIface = `
<node>
  <interface name="com.github.erdogan.EzanVaktiPro">
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
</node>`;

const EzanProxy = Gio.DBusProxy.makeProxyWrapper(EzanIface);

const PRAYER_ICONS = {
    'imsak': '🌙',
    'gunes': '🌅',
    'ogle': '☀️',
    'ikindi': '🌤️',
    'aksam': '🌇',
    'yatsi': '🌌'
};

const EzanIndicator = GObject.registerClass(
class EzanIndicator extends PanelMenu.Button {
    _init(extension) {
        super._init(0.0, 'Ezan Vakti Pro');
        this._ext = extension;

        // Container
        this._box = new St.BoxLayout({
            style_class: 'panel-status-indicators-box ezan-indicator-box'
        });

        this._iconLabel = new St.Label({
            text: '🕌',
            y_align: Clutter.ActorAlign.CENTER
        });

        this._timeLabel = new St.Label({
            text: 'Ezan Vakti',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'ezan-time-label'
        });

        this._box.add_child(this._iconLabel);
        this._box.add_child(this._timeLabel);
        this.add_child(this._box);

        this._buildMenu();
    }

    _buildMenu() {
        // Header (District + Hijri Date)
        this._headerItem = new PopupMenu.PopupMenuItem('🕌 Gölbaşı • Diyanet Takvimi', {
            reactive: false,
            can_focus: false,
            style_class: 'ezan-menu-header'
        });
        this.menu.addMenuItem(this._headerItem);

        // Countdown Subtitle
        this._countdownItem = new PopupMenu.PopupMenuItem('⏳ Vaktin Çıkmasına: --:--:--', {
            reactive: false,
            can_focus: false,
            style_class: 'ezan-menu-countdown'
        });
        this.menu.addMenuItem(this._countdownItem);

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        // 6 Prayer Times Items
        this._timeItems = {};
        const prayers = [
            ['imsak', '🌙 İmsak'],
            ['gunes', '🌅 Güneş'],
            ['ogle', '☀️ Öğle'],
            ['ikindi', '🌤️ İkindi'],
            ['aksam', '🌇 Akşam'],
            ['yatsi', '🌌 Yatsı']
        ];

        for (const [key, label] of prayers) {
            const item = new PopupMenu.PopupMenuItem(`${label}: --:--`, {
                reactive: false,
                can_focus: false
            });
            this.menu.addMenuItem(item);
            this._timeItems[key] = item;
        }

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        // Qibla Info
        this._qiblaItem = new PopupMenu.PopupMenuItem('🧭 Kıble Açısı: 153° • Saati: 11:25', {
            reactive: false,
            can_focus: false
        });
        this.menu.addMenuItem(this._qiblaItem);

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        // Submenu: Panel Yerleşimi (Sağ / Orta / Sol) - KULLANICI İSTEĞİ!
        this._posSubmenu = new PopupMenu.PopupSubMenuMenuItem('📍 Panel Konumu (Sağ / Orta / Sol)');
        
        this._posRightItem = new PopupMenu.PopupMenuItem('➡️ Sağ Taraf (Right)');
        this._posRightItem.connect('activate', () => this._ext.requestPosition('right'));
        this._posSubmenu.menu.addMenuItem(this._posRightItem);

        this._posCenterItem = new PopupMenu.PopupMenuItem('⏸️ Orta Kısım (Center)');
        this._posCenterItem.connect('activate', () => this._ext.requestPosition('center'));
        this._posSubmenu.menu.addMenuItem(this._posCenterItem);

        this._posLeftItem = new PopupMenu.PopupMenuItem('⬅️ Sol Taraf (Left)');
        this._posLeftItem.connect('activate', () => this._ext.requestPosition('left'));
        this._posSubmenu.menu.addMenuItem(this._posLeftItem);

        this.menu.addMenuItem(this._posSubmenu);

        // Sound Toggle
        this._soundItem = new PopupMenu.PopupMenuItem('🔔 Sesi Aç / Kapat');
        this._soundItem.connect('activate', () => this._ext.callMethod('ToggleSound'));
        this.menu.addMenuItem(this._soundItem);

        // Window Show/Hide
        this._windowItem = new PopupMenu.PopupMenuItem('🪟 Pencereyi Göster');
        this._windowItem.connect('activate', () => this._ext.showOrLaunchApp());
        this.menu.addMenuItem(this._windowItem);

        // Refresh Times
        this._refreshItem = new PopupMenu.PopupMenuItem('🔄 Vakitleri Güncelle');
        this._refreshItem.connect('activate', () => this._ext.callMethod('RefreshTimes'));
        this.menu.addMenuItem(this._refreshItem);

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        // Quit Completely
        this._quitItem = new PopupMenu.PopupMenuItem('❌ Uygulamayı Kapat');
        this._quitItem.connect('activate', () => {
            this._ext.callMethod('Quit');
            this.updateDisplayDisconnected();
        });
        this.menu.addMenuItem(this._quitItem);
    }

    updateStatus(nextName, nextTime, remSec, countdownStr, curName, distName, pos, soundEn, isVis) {
        // Top bar text
        this._iconLabel.set_text('🕌');
        this._timeLabel.set_text(`${nextName} ${countdownStr}`);

        // Update header & countdown
        this._headerItem.label.set_text(`🕌 ${distName} • Diyanet Takvimi`);
        this._countdownItem.label.set_text(`⏳ ${nextName} Vaktine: ${countdownStr}`);

        // Update sound item
        this._soundItem.label.set_text(soundEn ? '🔔 Ses: Açık (Kapat)' : '🔕 Ses: Kapalı (Aç)');

        // Update window item
        this._windowItem.label.set_text(isVis ? '🙈 Pencereyi Gizle' : '🪟 Pencereyi Göster');

        // Check active position item
        this._posRightItem.setOrnament(pos === 'right' ? PopupMenu.Ornament.CHECK : PopupMenu.Ornament.NONE);
        this._posCenterItem.setOrnament(pos === 'center' ? PopupMenu.Ornament.CHECK : PopupMenu.Ornament.NONE);
        this._posLeftItem.setOrnament(pos === 'left' ? PopupMenu.Ornament.CHECK : PopupMenu.Ornament.NONE);
    }

    updateTimes(imsak, gunes, ogle, ikindi, aksam, yatsi, qiblaTime, qiblaAngle, hijri) {
        if (this._timeItems['imsak']) this._timeItems['imsak'].label.set_text(`🌙 İmsak: ${imsak}`);
        if (this._timeItems['gunes']) this._timeItems['gunes'].label.set_text(`🌅 Güneş: ${gunes}`);
        if (this._timeItems['ogle']) this._timeItems['ogle'].label.set_text(`☀️ Öğle: ${ogle}`);
        if (this._timeItems['ikindi']) this._timeItems['ikindi'].label.set_text(`🌤️ İkindi: ${ikindi}`);
        if (this._timeItems['aksam']) this._timeItems['aksam'].label.set_text(`🌇 Akşam: ${aksam}`);
        if (this._timeItems['yatsi']) this._timeItems['yatsi'].label.set_text(`🌌 Yatsı: ${yatsi}`);

        this._qiblaItem.label.set_text(`🧭 Kıble Açısı: ${qiblaAngle}° • Saati: ${qiblaTime}`);
    }

    updateDisplayDisconnected() {
        this._iconLabel.set_text('🕌');
        this._timeLabel.set_text('Ezan Vakti');
        this._headerItem.label.set_text('🕌 Ezan Vakti Pro (Çevrimdışı)');
        this._countdownItem.label.set_text('⏳ Uygulamayı başlatmak için tıklayın');
        this._windowItem.label.set_text('🚀 Ezan Vakti Pro\'yu Başlat');
    }
});

export default class EzanVaktiExtension extends Extension {
    enable() {
        this._indicator = null;
        this._proxy = null;
        this._signalId = 0;
        this._posSignalId = 0;
        this._pollTimerId = 0;
        this._currentPosition = this._readInitialPosition();

        this._mountIndicator(this._currentPosition);
        this._initDBus();
    }

    disable() {
        if (this._pollTimerId) {
            GLib.source_remove(this._pollTimerId);
            this._pollTimerId = 0;
        }

        if (this._signalId && this._proxy) {
            this._proxy.disconnectSignal(this._signalId);
            this._signalId = 0;
        }

        if (this._posSignalId && this._proxy) {
            this._proxy.disconnectSignal(this._posSignalId);
            this._posSignalId = 0;
        }

        if (this._indicator) {
            this._indicator.destroy();
            this._indicator = null;
        }

        this._proxy = null;
    }

    _readInitialPosition() {
        try {
            const configPath = GLib.build_filenamev([GLib.get_home_dir(), '.config', 'ezan-vakti-pro', 'config.json']);
            if (GLib.file_test(configPath, GLib.FileTest.EXISTS)) {
                const [ok, contents] = GLib.file_get_contents(configPath);
                if (ok) {
                    const decoder = new TextDecoder('utf-8');
                    const cfg = JSON.parse(decoder.decode(contents));
                    if (['left', 'center', 'right'].includes(cfg.panel_position)) {
                        return cfg.panel_position;
                    }
                }
            }
        } catch (e) {
            // Ignore
        }
        return 'right';
    }

    _mountIndicator(boxName) {
        if (this._indicator) {
            this._indicator.destroy();
            this._indicator = null;
        }

        this._currentPosition = boxName;
        this._indicator = new EzanIndicator(this);
        Main.panel.addToStatusArea('ezan-vakti-pro', this._indicator, 1, boxName);
    }

    requestPosition(newBox) {
        if (['left', 'center', 'right'].includes(newBox)) {
            this._mountIndicator(newBox);
            this.callMethod('SetPanelPosition', new GLib.Variant('(s)', [newBox]));
            this._fetchTimesAndStatus();
        }
    }

    _initDBus() {
        try {
            this._proxy = new EzanProxy(
                Gio.DBus.session,
                BUS_NAME,
                OBJECT_PATH,
                (proxy, error) => {
                    if (error) {
                        if (this._indicator) this._indicator.updateDisplayDisconnected();
                        return;
                    }
                    this._onProxyReady();
                }
            );
        } catch (e) {
            if (this._indicator) this._indicator.updateDisplayDisconnected();
        }

        // 3-second heartbeat poll
        this._pollTimerId = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 3, () => {
            this._fetchTimesAndStatus();
            return GLib.SOURCE_CONTINUE;
        });
    }

    _onProxyReady() {
        if (!this._proxy) return;

        // StatusChanged signal
        this._signalId = this._proxy.connectSignal('StatusChanged', (proxy, senderName, [nextName, nextTime, remSec, countdownStr, curName, distName, pos, soundEn, isVis]) => {
            if (pos && pos !== this._currentPosition) {
                this._mountIndicator(pos);
            }
            if (this._indicator) {
                this._indicator.updateStatus(nextName, nextTime, remSec, countdownStr, curName, distName, pos, soundEn, isVis);
            }
        });

        // PanelPositionChanged signal
        this._posSignalId = this._proxy.connectSignal('PanelPositionChanged', (proxy, senderName, [newPos]) => {
            if (newPos && newPos !== this._currentPosition) {
                this._mountIndicator(newPos);
                this._fetchTimesAndStatus();
            }
        });

        this._fetchTimesAndStatus();
    }

    _fetchTimesAndStatus() {
        if (!this._proxy) return;

        // Pull Status
        this._proxy.GetStatusRemote((result, error) => {
            if (error || !result) {
                if (this._indicator) this._indicator.updateDisplayDisconnected();
                return;
            }
            const [nextName, nextTime, remSec, countdownStr, curName, distName, pos, soundEn, isVis] = result;
            if (pos && pos !== this._currentPosition) {
                this._mountIndicator(pos);
            }
            if (this._indicator) {
                this._indicator.updateStatus(nextName, nextTime, remSec, countdownStr, curName, distName, pos, soundEn, isVis);
            }
        });

        // Pull Today Times
        this._proxy.GetTodayTimesRemote((result, error) => {
            if (error || !result) return;
            const [imsak, gunes, ogle, ikindi, aksam, yatsi, qiblaTime, qiblaAngle, hijri] = result;
            if (this._indicator) {
                this._indicator.updateTimes(imsak, gunes, ogle, ikindi, aksam, yatsi, qiblaTime, qiblaAngle, hijri);
            }
        });
    }

    callMethod(methodName, param = null) {
        if (!this._proxy) return;
        try {
            if (param) {
                this._proxy[`${methodName}Remote`](param, () => {});
            } else {
                this._proxy[`${methodName}Remote`](() => {});
            }
        } catch (e) {
            console.error(`EzanVaktiPro error calling ${methodName}:`, e);
        }
    }

    showOrLaunchApp() {
        if (this._proxy) {
            this.callMethod('ShowWindow');
        } else {
            try {
                const appInfo = Gio.AppInfo.create_from_commandline(
                    'ezan-vakti-pro',
                    'Ezan Vakti Pro',
                    Gio.AppInfoCreateFlags.NONE
                );
                appInfo.launch([], null);
            } catch (e) {
                GLib.spawn_command_line_async('ezan-vakti-pro');
            }
        }
    }
}
