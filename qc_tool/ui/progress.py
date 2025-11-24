# qc_tool/ui/progress.py
import tkinter as tk
from queue import Queue
from pathlib import Path

class ProgressUI:
    """
    Ventana de progreso hecha solo con Tk (sin ttk).
    Corre en el hilo principal. Las tareas pesadas van en un thread y
    llaman set_message()/done().
    """
    def __init__(self, title="Procesando QC", subtitle="Aguarde…"):
        self._q = Queue()
        self.root = tk.Tk()
        self.root.title(title)
        self.root.resizable(False, False)
        self.root.geometry("420x150")
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)  # no permitir cerrar

        # Ícono si está
        try:
            base = Path(__file__).resolve().parents[2]
            for p in (base/"assets"/"logo_at.ico", base/"logo_at.ico"):
                if p.exists():
                    self.root.iconbitmap(str(p))
                    break
        except Exception:
            pass

        # ---- UI ----
        self.title_lbl = tk.Label(self.root, text="Aguarde…",
                                  font=("Segoe UI", 12, "bold"))
        self.title_lbl.pack(anchor="w", padx=16, pady=(14, 0))

        self.msg_var = tk.StringVar(value=subtitle)
        self.msg_lbl = tk.Label(self.root, textvariable=self.msg_var,
                                font=("Segoe UI", 10))
        self.msg_lbl.pack(anchor="w", padx=16, pady=(4, 8))

        # Barra animada (canvas)
        self.canvas = tk.Canvas(self.root, width=388, height=14, bg="#e5e5e5",
                                highlightthickness=0)
        self.canvas.pack(padx=16, fill="x")
        self.bar = self.canvas.create_rectangle(-80, 2, 40, 12, fill="#3399ff", width=0)
        self._dx = 5
        self._animating = True
        self._animate()

        # centrar
        self.root.update_idletasks()
        w, h = 420, 150
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x, y = (sw - w)//2, (sh - h)//3
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # loop de mensajes
        self.root.after(100, self._poll)

    # --- animación simple tipo “indeterminate” ---
    def _animate(self):
        if not self._animating:
            return
        self.canvas.move(self.bar, self._dx, 0)
        x1, _, x2, _ = self.canvas.coords(self.bar)
        W = int(self.canvas["width"])
        if x1 > W:
            self.canvas.coords(self.bar, -80, 2, 40, 12)
        self.root.after(30, self._animate)

    # --- cola de mensajes desde el worker ---
    def _poll(self):
        try:
            while True:
                cmd, arg = self._q.get_nowait()
                if cmd == "msg":
                    self.msg_var.set(arg)
                elif cmd == "done":
                    self._animating = False
                    self.msg_var.set(arg or "OK")
                    self.root.after(1200, self.root.destroy)
                elif cmd == "close":
                    self._animating = False
                    self.root.destroy()
        except Exception:
            pass
        finally:
            if self.root.winfo_exists():
                self.root.after(100, self._poll)

    def set_message(self, text: str):
        self._q.put(("msg", text))

    def done(self, text: str = "OK"):
        self._q.put(("done", text))

    def close_now(self):
        self._q.put(("close", None))

    def mainloop(self):
        self.root.mainloop()
