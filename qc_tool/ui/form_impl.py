from __future__ import annotations
from pathlib import Path
import tkinter as tk
import sys  
from tkinter import PhotoImage, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# ========= Paleta base =========
BG_COLOR    = "#010b46"   # azul corporativo
FG_COLOR    = "#FFFFFF"   # texto sobre azul
ACCENT      = "#FF8000"   # naranja

# ========= Paths ícono/logo =========
BASE_DIR = Path(__file__).resolve().parents[2]
_ICON_CANDIDATES = [BASE_DIR / "assets" / "logo_at.ico", BASE_DIR / "logo_at.ico"]
_PNG_CANDIDATES  = [BASE_DIR / "assets" / "logo_at.png", BASE_DIR / "logo_at.png"]

def _first_that_exists(paths):
    for p in paths:
        if p.exists():
            return str(p)
    return ""

ICON_PATH = _first_that_exists(_ICON_CANDIDATES)
LOGO_PATH = _first_that_exists(_PNG_CANDIDATES)

# ========= Tooltip simple =========
class Tooltip:
    def __init__(self, widget, text: str, delay_ms: int = 300):
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self._after = None
        self._tip: tk.Toplevel | None = None
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, _):
        self._after = self.widget.after(self.delay_ms, self._show)

    def _on_leave(self, _):
        if self._after:
            self.widget.after_cancel(self._after)
            self._after = None
        self._hide()

    def _show(self):
        if self._tip:  # ya visible
            return
        self._tip = tk.Toplevel(self.widget)
        self._tip.overrideredirect(True)
        self._tip.attributes("-topmost", True)
        # posicion
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self._tip.geometry(f"+{x}+{y}")
        # contenido
        frm = ttk.Frame(self._tip, padding=6, bootstyle="secondary")
        frm.pack()
        ttk.Label(frm, text=self.text).pack()

    def _hide(self):
        if self._tip:
            self._tip.destroy()
            self._tip = None

# ========= Helper lectura segura (por si algún widget ya no existe) =========
def _safe_get(widget, default=""):
    try:
        return widget.get().strip()
    except Exception:
        return default


class QCForm(ttk.Window):
    def __init__(self):
        # tema neutro; forzamos paleta propia con estilos
        super().__init__(themename="flatly")
        self.title("QC byGasti")
        self.geometry("840x760")
        self.minsize(760, 660)
        # Escala HiDPI suave
        try:
            self.call("tk", "scaling", 1.2)
        except Exception:
            pass

        if ICON_PATH:
            try:
                self.iconbitmap(ICON_PATH)
            except Exception:
                pass

        self._init_styles()
        self._build_ui()
        self._set_app_icon()   # ícono para ventana, barra de tareas y messagebox
        self._center_on_screen()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)  # no destruir con la X

        # atajos
        self.bind("<Return>", lambda e: self._on_submit())
        self.bind("<Escape>", lambda e: self._on_cancel())

    # ---------- helpers ----------
    def _center_on_screen(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 3
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _set_app_icon(self):
        """Fija icono (ventana, messagebox y taskbar) y lo mejora si hay solo PNG."""
        import os
        # 1) Si tenemos PNG, intentamos crear un .ico multi-res (mejor calidad en 16x16)
        try:
            if LOGO_PATH:
                from PIL import Image  # Pillow opcional
                auto_ico = BASE_DIR / "assets" / "logo_at_auto.ico"
                auto_ico.parent.mkdir(parents=True, exist_ok=True)
                im = Image.open(LOGO_PATH).convert("RGBA")
                sizes = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]
                im.save(auto_ico, format="ICO", sizes=sizes)
                ico_path = str(auto_ico)
            else:
                ico_path = ICON_PATH
        except Exception:
            ico_path = ICON_PATH  # sin Pillow, usamos el .ico existente si hay

        # 2) Tk: ícono de ventana + heredado a messagebox/Toplevel
        try:
            if ico_path:
                self.iconbitmap(ico_path)
        except Exception:
            pass
        try:
            if LOGO_PATH:
                self._app_icon_img = PhotoImage(file=LOGO_PATH)  # mantener ref
                self.wm_iconphoto(True, self._app_icon_img)
        except Exception:
            pass

        # 3) Mejor agrupación en taskbar
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AT.QCApp")
        except Exception:
            pass

        # 4) Forzar icono en taskbar con WinAPI (grande/chico)
        try:
            import ctypes
            if ico_path and os.path.exists(ico_path):
                self.update_idletasks()
                HWND = self.winfo_id()
                WM_SETICON = 0x0080
                IMAGE_ICON = 1
                LR_LOADFROMFILE = 0x0010
                LR_DEFAULTSIZE  = 0x0040

                LoadImageW = ctypes.windll.user32.LoadImageW
                SendMessageW = ctypes.windll.user32.SendMessageW

                # grande (usa mejor tamaño disponible)
                hbig = LoadImageW(0, ico_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE)
                # chico 16x16
                hsmall = LoadImageW(0, ico_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)

                if hbig:
                    SendMessageW(HWND, WM_SETICON, 1, hbig)
                if hsmall:
                    SendMessageW(HWND, WM_SETICON, 0, hsmall)
        except Exception:
            pass

    def _init_styles(self):
        s = ttk.Style()

        # Header azul
        s.configure("Header.TFrame", background=BG_COLOR)
        s.configure("Header.TLabel", background=BG_COLOR, foreground=FG_COLOR)
        s.configure("Title.TLabel",  background=BG_COLOR, foreground=FG_COLOR, font=("Segoe UI Semibold", 16))

        # Notebook (tab activo naranja)
        s.configure("AT.TNotebook", padding=0)
        s.configure("AT.TNotebook.Tab", padding=(18, 12), font=("Segoe UI", 10))
        s.map("AT.TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", "#ffffff")])

        # Tarjetas (secciones) – look limpio
        s.configure("Card.TFrame", relief="flat")
        s.configure("CardHead.TLabel", font=("Segoe UI Semibold", 11))
        s.configure("CardBody.TFrame", padding=12)
        s.configure("Field.TLabel", font=("Segoe UI", 11))
        s.configure("Small.TLabel", font=("Segoe UI", 10))

        # Botones
        s.configure("AT.TButton", font=("Segoe UI Semibold", 11), padding=10)
        s.configure("AT.Accent.TButton", font=("Segoe UI Semibold", 12), padding=12)
        s.map("AT.Accent.TButton",
              background=[("!disabled", ACCENT), ("active", "#ff9d3f")],
              foreground=[("!disabled", "#ffffff")])

        # Entry error (validación inline)
        s.configure("Error.TEntry", foreground="#ffffff")
        s.map("Error.TEntry", fieldbackground=[("!disabled", "#9c2b2e")])

        # Radios/toggles
        s.configure("AT.TRadiobutton", font=("Segoe UI", 10))

    # --- componentes reutilizables ---
    def _card(self, parent, title_text: str):
        """Tarjeta con título y cuerpo; devuelve el frame 'body' para poner contenido."""
        outer = ttk.Frame(parent, style="Card.TFrame")
        outer.pack(fill="x", padx=6, pady=6)

        head = ttk.Frame(outer)
        head.pack(fill="x", padx=2, pady=(2, 0))
        ttk.Label(head, text=title_text, style="CardHead.TLabel").pack(anchor="w")
        ttk.Separator(outer).pack(fill="x", padx=2, pady=(4, 0))

        body = ttk.Frame(outer, style="CardBody.TFrame")
        body.pack(fill="x")
        return body

    def _toggle_row(self, parent, label: str, varname: str, row: int):
        """
        Crea una fila con etiqueta + toggle Sí/No.
        Devuelve el Checkbutton y le cuelga la Label en .label_widget
        para poder cambiar el texto u ocultarla después.
        """
        var = ttk.StringVar(value="No")
        setattr(self, varname, var)

        lbl = ttk.Label(parent, text=label, style="Field.TLabel")
        lbl.grid(row=row, column=0, sticky="w", padx=8, pady=8)

        chk = ttk.Checkbutton(
            parent,
            variable=var,
            onvalue="Sí",
            offvalue="No",
            bootstyle="warning-round-toggle",
        )
        chk.grid(row=row, column=1, sticky="w", padx=8, pady=8)

        try:
            chk.configure(cursor="hand2")
        except Exception:
            pass

        # guardamos la label enganchada al check
        chk.label_widget = lbl
        return chk

    # ---------- UI ----------
    def _build_ui(self):
        # Header
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(side="top", fill="x")

        if LOGO_PATH:
            try:
                img = PhotoImage(file=LOGO_PATH).subsample(4, 4)
                llogo = ttk.Label(header, image=img, style="Header.TLabel")
                llogo.image = img
                llogo.pack(side="left", padx=14, pady=10)
            except Exception:
                pass

        ttk.Label(header, text="Formulario de Control de Calidad", style="Title.TLabel").pack(
            side="left", padx=8, pady=10
        )

        # Notebook
        nb = ttk.Notebook(self, style="AT.TNotebook", bootstyle="primary")
        nb.pack(fill="both", expand=True, padx=12, pady=12)

        tab_general  = ttk.Frame(nb)
        tab_hw       = ttk.Frame(nb)
        tab_sw       = ttk.Frame(nb)
        tab_sellos   = ttk.Frame(nb)

        nb.add(tab_general, text="🧾  General", padding=6, sticky="nsew")
        nb.add(tab_hw,      text="🖥️  Hardware", padding=6, sticky="nsew")
        nb.add(tab_sw,      text="⚙️  Software", padding=6, sticky="nsew")
        nb.add(tab_sellos,  text="🏷️  Sellos", padding=6, sticky="nsew")

        self._tab_general(tab_general)
        self._tab_hw(tab_hw)
        self._tab_sw(tab_sw)
        self._tab_sellos(tab_sellos)
        self._on_tipo_change()

        # Botonera
        bar = ttk.Frame(self)
        bar.pack(side="bottom", fill="x", padx=12, pady=(0, 0))
        ttk.Button(bar, text="Cancelar", bootstyle="secondary-outline",
                   command=self._on_cancel, style="AT.TButton").pack(side="right", padx=6)
        btn_ok = ttk.Button(bar, text="Continuar", command=self._on_submit,
                            style="AT.Accent.TButton", bootstyle="warning-pill")
        btn_ok.pack(side="right", padx=6)
        try:
            btn_ok.configure(cursor="hand2")
        except Exception:
            pass

        # Status bar
        status = ttk.Frame(self, bootstyle="secondary")
        status.pack(side="bottom", fill="x")
        self.status_var = ttk.StringVar(value="Listo • Enter = Continuar, Esc = Cancelar")
        ttk.Label(status, textvariable=self.status_var, padding=6).pack(side="left")

    # ======== Pestañas ========
    def _tab_general(self, parent):
        body = self._card(parent, "Tipo de equipo")
        self.tipo_var = ttk.StringVar(value="PC")
        rb_pc = ttk.Radiobutton(
            body, text="🖥️  PC", variable=self.tipo_var, value="PC",
            style="AT.TRadiobutton", bootstyle="warning-toolbutton",command=self._on_tipo_change, 
        )
        rb_pc.grid(row=0, column=0, sticky="w", padx=6, pady=8)
        rb_lap = ttk.Radiobutton(
            body, text="💻  Laptop", variable=self.tipo_var, value="LAP",
            style="AT.TRadiobutton", bootstyle="warning-toolbutton",command=self._on_tipo_change,
        )
        rb_lap.grid(row=0, column=1, sticky="w", padx=6, pady=8)
        for rb in (rb_pc, rb_lap):
            try:
                rb.configure(cursor="hand2")
            except Exception:
                pass

        info = self._card(parent, "Información QC")
        ttk.Label(info, text="👤 ¿Quién hace el QC?", style="Field.TLabel").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.entry_qc = ttk.Entry(info, width=40)
        self.entry_qc.grid(row=0, column=1, sticky="ew", padx=8, pady=8)

        ttk.Label(info, text="🏢 Cliente:", style="Field.TLabel").grid(row=1, column=0, sticky="w", padx=8, pady=8)
        self.entry_cliente = ttk.Entry(info, width=40)
        self.entry_cliente.grid(row=1, column=1, sticky="ew", padx=8, pady=8)

        # tooltips
        Tooltip(self.entry_qc, "Nombre de quien realiza el control de calidad")
        Tooltip(self.entry_cliente, "Cliente para el que se realiza el QC")

        info.columnconfigure(1, weight=1)

    def _tab_hw(self, parent):
        g = self._card(parent, "Hardware")

        ttk.Label(g, text="🔌 Puertos USB:", style="Field.TLabel").grid(
            row=0, column=0, sticky="w", padx=8, pady=8
        )
        self.entry_usb = ttk.Spinbox(g, from_=0, to=20, width=6)
        self.entry_usb.insert(0, "0")
        self.entry_usb.grid(row=0, column=1, sticky="w", padx=8, pady=8)
        Tooltip(self.entry_usb, "Cantidad de puertos USB visibles (frente/trasera)")

        # toggles
        self.chk_dvd = self._toggle_row(g, "💿 Lectora DVD:", "dvd_var", 1)
        self.chk_cable = self._toggle_row(g, "🔌 Cable de poder:", "cable_var", 2)
        self.chk_hdmi = self._toggle_row(g, "📺 HDMI:", "hdmi_var", 3)
        self.chk_rj45 = self._toggle_row(g, "🌐 RJ45:", "rj45_var", 4)
        # solo aplican a Laptop (los vamos a ocultar en PC)
        self.chk_teclado = self._toggle_row(g, "⌨️ Teclado (testear):", "teclado_var", 5)
        self.chk_webcam = self._toggle_row(g, "📷 Webcam:", "webcam_var", 6)

        for t in (
            self.chk_dvd,
            self.chk_cable,
            self.chk_hdmi,
            self.chk_rj45,
            self.chk_teclado,
            self.chk_webcam,
        ):
            Tooltip(t, "Alterná entre Sí / No")

        g.columnconfigure(1, weight=1)


    def _tab_sw(self, parent):
        g = self._card(parent, "Software")
        t1 = self._toggle_row(g, "🧰 Drivers actualizados (Verificar):", "drivers_var", 0)
        t2 = self._toggle_row(g, "📶 WiFi funcionando:", "wifi_var", 1)
        for t in (t1, t2):
            Tooltip(t, "Alterná entre Sí / No")
        g.columnconfigure(1, weight=1)

    def _tab_sellos(self, parent):
        g = self._card(parent, "Chequeo de sellos")
        t1 = self._toggle_row(g, "🏷️ AT Service:", "atservice_var", 0)
        t2 = self._toggle_row(g, "🧠 Micro Intel/AMD:", "micro_var", 1)
        t3 = self._toggle_row(g, "✅ Sello Garantía:", "garantia_var", 2)
        t4 = self._toggle_row(g, "🪟 COA Windows:", "coa_var", 3)
        for t in (t1, t2, t3, t4):
            Tooltip(t, "Alterná entre Sí / No")
        g.columnconfigure(1, weight=1)
    
    def _on_tipo_change(self):
        """Se llama al cambiar entre PC / Laptop."""
        tipo = self.tipo_var.get()

        # Cambiar texto Cable de poder ↔ Cargador
        if hasattr(self, "chk_cable"):
            lbl = getattr(self.chk_cable, "label_widget", None)
            if lbl is not None:
                if tipo == "LAP":
                    lbl.configure(text="🔌 Cargador:")
                else:
                    lbl.configure(text="🔌 Cable de poder:")

        # Teclado / Webcam: solo visibles en Laptop
        for nombre_chk, nombre_var in (("chk_teclado", "teclado_var"), ("chk_webcam", "webcam_var")):
            chk = getattr(self, nombre_chk, None)
            var = getattr(self, nombre_var, None)
            if chk is None or var is None:
                continue
            lbl = getattr(chk, "label_widget", None)
            if tipo == "LAP":
                # mostrar
                if lbl is not None:
                    lbl.grid()
                chk.grid()
            else:
                # ocultar y resetear a "No"
                if lbl is not None:
                    lbl.grid_remove()
                chk.grid_remove()
                var.set("No")


    def _update_tipo_equipo_ui(self):
        """Ajusta texto de Cable/Cargador y visibilidad de Teclado/Webcam según tipo."""
        tipo = self.tipo_var.get()

        meta = getattr(self, "_toggle_meta", {})

        # 🔌 Cable de poder ↔ Cargador
        cab = meta.get("cable_var")
        if cab:
            lbl = cab["label"]
            if tipo == "LAP":
                lbl.configure(text="🔌 Cargador:")
            else:
                lbl.configure(text="🔌 Cable de poder:")

        # ⌨️ / 📷 Teclado + Webcam: solo visibles en Laptop
        for name in ("teclado_var", "webcam_var"):
            m = meta.get(name)
            if not m:
                continue
            lbl = m["label"]
            chk = m["check"]
            if tipo == "LAP":
                # volver a mostrar (usan el grid original)
                lbl.grid()
                chk.grid()
            else:
                # ocultar en PC
                lbl.grid_remove()
                chk.grid_remove()
                getattr(self, name).set("No")

    # ======== Validación & acciones ========
    def _validate(self) -> bool:
        ok = True
        # reset estilos por si venían en error
        self.entry_qc.configure(style="TEntry")
        self.entry_cliente.configure(style="TEntry")

        if not self.entry_qc.get().strip():
            self.entry_qc.configure(style="Error.TEntry")
            messagebox.showwarning("Faltan datos", "Completá quién hace el QC.", parent=self)
            self.entry_qc.focus_set()
            self.status_var.set("Falta completar: ¿Quién hace el QC?")
            ok = False

        if ok and not self.entry_cliente.get().strip():
            self.entry_cliente.configure(style="Error.TEntry")
            messagebox.showwarning("Faltan datos", "Completá el cliente.", parent=self)
            self.entry_cliente.focus_set()
            self.status_var.set("Falta completar: Cliente")
            ok = False

        if ok:
            self.status_var.set("v2.0")
        return ok

    def _on_submit(self):
        if self._validate():
            self.quit()

    def _on_cancel(self):
        self.tipo_var.set("CANCEL")
        self.quit()


# ======== API para el pipeline ========
def obtener_datos_formulario():
    app = QCForm()
    app.mainloop()

    # 👉 Si se canceló (botón Cancelar o cerrar ventana), terminar el programa
    try:
        tipo = app.tipo_var.get()
    except Exception:
        tipo = "CANCEL"

    if tipo == "CANCEL":
        try:
            app.destroy()
        except Exception:
            pass
        # Sale del proceso completo: no se ejecuta el pipeline ni la barra de carga
        sys.exit(0)

    # Si no se canceló, armamos el diccionario con los datos del formulario
    data = {
        "Tipo de equipo": app.tipo_var.get(),
        "QC realizado por": _safe_get(app.entry_qc),
        "Cliente": _safe_get(app.entry_cliente),
        "Puertos USB": _safe_get(app.entry_usb),
        "Lectora DVD": app.dvd_var.get(),
        "Cable de poder": app.cable_var.get(),     # la etiqueta visual ya cambia a Cargador
        "HDMI": app.hdmi_var.get(),
        "RJ45": app.rj45_var.get(),
        "Teclado (Testear)": getattr(app, "teclado_var", ttk.StringVar(value="No")).get(),
        "Webcam": getattr(app, "webcam_var", ttk.StringVar(value="No")).get(),
        "Drivers OK": app.drivers_var.get(),
        "WiFi funcionando": app.wifi_var.get(),
        "AT Service": app.atservice_var.get(),
        "Micro Intel/AMD": app.micro_var.get(),
        "Sello Garantía": app.garantia_var.get(),
        "COA Windows": app.coa_var.get(),
    }
    try:
        app.destroy()
    except Exception:
        pass
    return data

if __name__ == "__main__":
    d = obtener_datos_formulario()
    for k, v in d.items():
        print(f"{k}: {v}")
