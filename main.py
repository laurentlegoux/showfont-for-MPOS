from mpos import Activity, FontManager 
import mpos.ui  
import lvgl as lv  
  
FULL_RANGES = (  
    (0x20, 0x7F), (0xA0, 0x180), (0x2000, 0x2070),  
    (0x20A0, 0x20D0), (0x2100, 0x2150), (0x2190, 0x2200),  
    (0x2200, 0x2300), (0x2300, 0x2400), (0x2460, 0x2500),  
    (0x25A0, 0x2600), (0x2600, 0x2700), (0x2B00, 0x2C00),  
    (0xF000, 0xF800),  
)  
PICKER_RANGES = ((0xF000, 0xF800),)  
  
CELL = 48  
  
class Main(Activity):  
  
    # ---------- widget helpers ----------  
    def _cell(self, parent, glyph, font, snippet):  
        c = lv.obj(parent)  
        c.set_size(CELL, CELL)  
        c.set_style_pad_all(0, lv.PART.MAIN)  
        l = lv.label(c)  
        l.set_style_text_font(font, lv.PART.MAIN)  
        l.set_text(glyph)  
        l.center()  
        def cb(e, s=snippet):  
            self.detail.set_text(s)  
        c.add_event_cb(cb, lv.EVENT.CLICKED, None)  
  
    def _grid(self, parent):  
        g = lv.obj(parent)  
        g.set_width(lv.pct(100))  
        g.set_height(lv.SIZE_CONTENT)  
        g.set_flex_flow(lv.FLEX_FLOW.ROW_WRAP)  
        g.set_style_pad_all(2, lv.PART.MAIN)  
        g.set_style_border_width(0, lv.PART.MAIN)  
        return g  
  
    def _title(self, parent, text):  
        t = lv.label(parent)  
        t.set_text("=== {} ===".format(text))  
        t.set_style_text_font(lv.font_montserrat_14, lv.PART.MAIN)  
        t.set_width(lv.pct(100))  
  
    def _glyphs_of(self, font, ranges):  
        dsc = lv.font_glyph_dsc_t()  
        out = []  
        for start, end in ranges:  
            for cp in range(start, end):  
                if font.get_glyph_dsc(font, dsc, cp, cp):  
                    out.append(cp)  
        return out  
  
    # ---------- Tab 1: all chars for chosen font/size ----------  
    def _build_fonts_tab(self, tab):  
        tab.set_flex_flow(lv.FLEX_FLOW.COLUMN)  
        tab.set_scroll_dir(lv.DIR.VER)  
        tab.set_scrollbar_mode(lv.SCROLLBAR_MODE.AUTO)  
        tab.set_style_pad_all(4, lv.PART.MAIN)  
  
        # Collect distinct families and sizes from listFonts()  
        self._families = []  
        self._sizes = []  
        for info in FontManager.listFonts():  
            if info["family"] not in self._families:  
                self._families.append(info["family"])  
            if info["size"] not in self._sizes:  
                self._sizes.append(info["size"])  
  
        row = lv.obj(tab)  
        row.set_width(lv.pct(100))  
        row.set_height(lv.SIZE_CONTENT)  
        row.set_flex_flow(lv.FLEX_FLOW.ROW)  
        row.set_style_border_width(0, lv.PART.MAIN)  
  
        self.family_dd = lv.dropdown(row)  
        self.family_dd.set_options("\n".join(self._families))  
        self.family_dd.set_width(lv.pct(48))  
        self.family_dd.add_event_cb(self._font_sel_changed,  
                                    lv.EVENT.VALUE_CHANGED, None)  
  
        self.size_dd = lv.dropdown(row)  
        self.size_dd.set_options("\n".join(str(s) for s in self._sizes))  
        self.size_dd.set_width(lv.pct(48))  
        self.size_dd.add_event_cb(self._font_sel_changed,  
                                  lv.EVENT.VALUE_CHANGED, None)  
  
        self.glyphs_info = lv.label(tab)  
        self.glyphs_info.set_width(lv.pct(100))  
        self.glyphs_info.set_long_mode(lv.label.LONG_MODE.WRAP)  
        self.glyphs_info.set_style_text_font(lv.font_montserrat_12, lv.PART.MAIN)  
  
        self.glyphs_lbl = lv.label(tab)  
        self.glyphs_lbl.set_width(lv.pct(99))  
        self.glyphs_lbl.set_long_mode(lv.label.LONG_MODE.WRAP)  
  
        self._show_font_glyphs()  
  
    def _font_sel_changed(self, e):  
        self._show_font_glyphs()  
  
    def _show_font_glyphs(self):  
        family = self._families[self.family_dd.get_selected()]  
        size = self._sizes[self.size_dd.get_selected()]  
        font = FontManager.getFont(size=size, family=family)  
        cps = self._glyphs_of(font, FULL_RANGES)  
        self.glyphs_lbl.set_style_text_font(font, lv.PART.MAIN)  
        self.glyphs_lbl.set_text(" ".join(chr(cp) for cp in cps))  
        self.glyphs_info.set_text(  
            '{} glyphs — getFont(size={}, family="{}")'.format(  
                len(cps), size, family))  
        self.detail.set_text('getFont(size={}, family="{}")'.format(  
            size, family))  
  
    # ---------- Tab 2: picker (unchanged logic) ----------  
    def _build_picker_tab(self, tab):  
        tab.set_flex_flow(lv.FLEX_FLOW.COLUMN)  
        tab.set_scroll_dir(lv.DIR.VER)  
        tab.set_scrollbar_mode(lv.SCROLLBAR_MODE.AUTO)  
        tab.set_style_pad_all(4, lv.PART.MAIN)  
  
        emoji_font = FontManager.getFont(size=16, family="Montserrat", emoji=True)  
        base_font  = FontManager.getFont(size=16, family="Montserrat")  
  
        self._title(tab, "LVGL SYMBOLS")  
        g = self._grid(tab)  
        for name in dir(lv.SYMBOL):  
            if not name.startswith("_"):  
                sym = getattr(lv.SYMBOL, name)  
                cp = "{:X}".format(ord(sym))  
                self._cell(g, sym, base_font,  
                    'lv.SYMBOL.{}   U+{}   "\\u{}"'.format(name, cp, cp.lower()))  
  
        self._title(tab, "MPOS SYMBOLS")  
        g = self._grid(tab)  
        for name in mpos.ui.__all__:  
            val = getattr(mpos.ui, name)  
            if isinstance(val, str) and "SYMBOL" in name:  
                esc = "".join("\\u{:04x}".format(ord(c)) for c in val)  
                self._cell(g, val, base_font,  
                    'mpos.ui.{}   "{}"'.format(name, esc))  
  
        self._title(tab, "EMOJIS")  
        g = self._grid(tab)  
        for e in FontManager.getEmojiStrings():  
            esc = "".join("\\U{:08x}".format(ord(c)) for c in e)  
            self._cell(g, e, emoji_font,  
                '"{}"  needs getFont(emoji=True)'.format(esc))  
  
        self._title(tab, "ICONS PER FONT")  
        for info in FontManager.listFonts():  
            self._title(tab, info["name"])  
            g = self._grid(tab)  
            font_desc = 'getFont(size={}, family="{}")'.format(  
                info["size"], info["family"])  
            for cp in self._glyphs_of(info["base_font"], PICKER_RANGES):  
                self._cell(g, chr(cp), info["base_font"],  
                           '{}  "\\u{:04x}"'.format(font_desc, cp))  
  
    # ---------- shell ----------  
    def onCreate(self):  
        screen = lv.obj()  
        screen.set_flex_flow(lv.FLEX_FLOW.COLUMN)  
        screen.remove_flag(lv.obj.FLAG.SCROLLABLE)  
        screen.set_style_pad_all(0, lv.PART.MAIN)  
  
        # Fixed detail bar — always visible on both tabs  
        self.detail = lv.label(screen)  
        self.detail.set_text("Tap a glyph to see its snippet")  
        self.detail.set_width(lv.pct(100))  
        self.detail.set_long_mode(lv.label.LONG_MODE.WRAP)  
        self.detail.set_style_text_font(lv.font_montserrat_14, lv.PART.MAIN)  
        self.detail.set_style_border_width(1, lv.PART.MAIN)  
        self.detail.set_style_border_side(lv.BORDER_SIDE.BOTTOM, lv.PART.MAIN)  
  
        # Tabview fills the rest  
        tv = lv.tabview(screen)  
        tv.set_flex_grow(1)  
        tv.set_width(lv.pct(100))  
        tv.set_tab_bar_size(36)  
  
        tab_fonts  = tv.add_tab("Installed Fonts")  
        tab_picker = tv.add_tab("Graph Picker")  
  
        self._build_fonts_tab(tab_fonts)  
        self._build_picker_tab(tab_picker)  
  
        self.setContentView(screen)
