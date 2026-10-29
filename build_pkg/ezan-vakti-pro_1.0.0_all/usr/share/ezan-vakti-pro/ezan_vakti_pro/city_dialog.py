import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

QUICK_CITIES = [
    ("Gölbaşı", "ANKARA", "506", "GÖLBAŞI", "9206"),
    ("Ankara", "ANKARA", "506", "ANKARA", "9206"),
    ("İstanbul", "İSTANBUL", "539", "İSTANBUL", "9541"),
    ("İzmir", "İZMİR", "540", "İZMİR", "9560"),
    ("Bursa", "BURSA", "516", "BURSA", "9335"),
    ("Konya", "KONYA", "548", "KONYA", "9676"),
    ("Antalya", "ANTALYA", "507", "ANTALYA", "9225")
]

def open_city_dialog(parent_window, storage_manager, diyanet_client, prayer_engine, on_city_changed=None):
    dlg = Adw.AlertDialog.new(
        "Şehir / İlçe Değiştir",
        "Diyanet vakitleri için il veya ilçe arayın veya listeden seçin."
    )
    dlg.add_response("close", "Kapat")
    dlg.set_default_response("close")

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_size_request(380, 420)
    box.set_margin_top(8)
    box.set_margin_bottom(8)
    box.set_margin_start(12)
    box.set_margin_end(12)

    # 1. Auto-detect button
    auto_btn = Gtk.Button()
    auto_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    auto_box.set_halign(Gtk.Align.CENTER)
    auto_box.append(Gtk.Image.new_from_icon_name("find-location-symbolic"))
    auto_box.append(Gtk.Label(label="📍 Otomatik Konum Belirle (GPS / IP)"))
    auto_btn.set_child(auto_box)
    auto_btn.add_css_class("suggested-action")
    box.append(auto_btn)

    # 2. Search Entry
    search_entry = Gtk.SearchEntry()
    search_entry.set_placeholder_text("İl veya ilçe adı yazın (Örn: Gölbaşı, Kadıköy, Konya)...")
    box.append(search_entry)

    # 3. Quick Chips
    quick_box = Gtk.FlowBox()
    quick_box.set_selection_mode(Gtk.SelectionMode.NONE)
    quick_box.set_max_children_per_line(4)
    quick_box.set_column_spacing(6)
    quick_box.set_row_spacing(6)

    for disp, cname, cid, dname, did in QUICK_CITIES:
        btn = Gtk.Button(label=disp)
        btn.add_css_class("flat")
        btn.connect("clicked", lambda b, d=disp, c=cname, ci=cid, dn=dname, di=did: _select_location(dlg, storage_manager, prayer_engine, on_city_changed, d, c, ci, dn, di))
        quick_box.append(btn)
    box.append(quick_box)

    # 4. Results Scroller
    scroller = Gtk.ScrolledWindow()
    scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroller.set_vexpand(True)

    results_list = Gtk.ListBox()
    results_list.add_css_class("boxed-list")
    scroller.set_child(results_list)
    box.append(scroller)

    def _populate_results(query=""):
        while child := results_list.get_first_child():
            results_list.remove(child)

        items = diyanet_client.search_locations(query) if query else []
        if not items and query:
            empty_row = Adw.ActionRow()
            empty_row.set_title("Eşleşen ilçe bulunamadı.")
            results_list.append(empty_row)
            return

        for item in items:
            row = Adw.ActionRow()
            row.set_title(item["display_name"])
            row.set_subtitle(f"Diyanet İlçe Kodu: {item['district_id']}")
            row.set_activatable(True)

            btn = Gtk.Button(label="Seç")
            btn.set_valign(Gtk.Align.CENTER)
            btn.add_css_class("btn-secondary")
            row.add_suffix(btn)

            row.connect("activated", lambda r, it=item: _select_location(
                dlg, storage_manager, prayer_engine, on_city_changed,
                it["district_name"], it["city_name"], it["city_id"], it["district_name"], it["district_id"]
            ))
            btn.connect("clicked", lambda b, it=item: _select_location(
                dlg, storage_manager, prayer_engine, on_city_changed,
                it["district_name"], it["city_name"], it["city_id"], it["district_name"], it["district_id"]
            ))
            results_list.append(row)

    search_entry.connect("search-changed", lambda e: _populate_results(e.get_text()))

    def _on_auto_detect(b):
        loc = diyanet_client.detect_ip_location()
        city_name = loc.get("city", "Ankara")
        _select_location(dlg, storage_manager, prayer_engine, on_city_changed, city_name, city_name, "506", city_name, "9206")

    auto_btn.connect("clicked", _on_auto_detect)

    dlg.set_extra_child(box)
    dlg.choose(parent_window, None, lambda d, r: None)

def _select_location(dlg, storage, engine, on_changed, disp, cname, cid, dname, did):
    cfg = storage.config
    cfg["display_name"] = disp.capitalize()
    cfg["city"] = cname
    cfg["city_id"] = cid
    cfg["district"] = dname
    cfg["district_id"] = did
    storage.save_config()

    engine.refresh_vakitler_if_needed(force=True)

    if on_changed:
        on_changed()

    dlg.force_close()
