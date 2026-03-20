# src/interfaz.py
from __future__ import annotations
import sys
import time
import traceback
import faulthandler
from pathlib import Path
from queue import Queue

fatal_log = open("crash_fatal_c.txt", "a", encoding="utf-8")
fatal_log.write("--- INICIANDO NUEVA SESION DE FAULTHANDLER ---\n")
faulthandler.enable(file=fatal_log, all_threads=True)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QStackedWidget, QFrame, QLineEdit,
    QButtonGroup, QGridLayout, QScrollArea,
    QMessageBox, QDialog, QProgressBar, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QIcon, QFont, QColor
from PyQt6.QtCore import Qt, QTimer, QEvent, pyqtSignal

# 🟢 LAZY LOADING: Eliminamos la importación de src.pruebas de acá arriba 
# para que no frene el arranque de la aplicación.

from src.modelos import DatosFormulario
from src.configuracion import DIR_ASSETS
from src.botones import LiquidSidebarButton, LiquidGridButton, LiquidSubmitButton, InstagramPollSwitch

class ProgressUI(QDialog):
    # 🟢 SEÑALES NATIVAS: Transportan la info del hilo al hilo principal
    senal_mensaje = pyqtSignal(str)
    senal_fin = pyqtSignal(str, str, str) # Mensaje barra, Titulo Cartel, Mensaje Cartel

    def __init__(self, title="Motor de Extracción", subtitle="Aguarde…", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(350, 130)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        
        self.setStyleSheet("""
            QDialog { background-color: #ffffff; border-radius: 8px; border: 1px solid #e0e0e0; }
            QLabel { color: #222222; font-family: 'Segoe UI'; }
            QProgressBar { border: 1px solid #e0e0e0; border-radius: 4px; background-color: #f5f5f5; color: transparent; }
            QProgressBar::chunk { background-color: #1A2865; border-radius: 3px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(lbl_title)

        self.lbl_msg = QLabel(subtitle)
        self.lbl_msg.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.lbl_msg)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(10)
        layout.addWidget(self.progress)

        # Conectar señales
        self.senal_mensaje.connect(self._actualizar_mensaje)
        self.senal_fin.connect(self._finalizar)

    def _actualizar_mensaje(self, texto):
        self.lbl_msg.setText(texto)

    def _finalizar(self, texto, titulo_popup, mensaje_popup):
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.lbl_msg.setText(texto)
        
        def mostrar_popup():
            if titulo_popup and mensaje_popup:
                if "Error" in titulo_popup:
                    QMessageBox.critical(None, titulo_popup, mensaje_popup)
                else:
                    QMessageBox.information(None, titulo_popup, mensaje_popup)

        # Retraso para que la barra desaparezca antes del cartel
        QTimer.singleShot(200, mostrar_popup)
        self.accept()

    # Métodos que llama el Pipeline
    def set_message(self, text): 
        self.senal_mensaje.emit(text)
        
    def finalizar_proceso(self, text="Finalizado", titulo_popup="", mensaje_popup=""): 
        self.senal_fin.emit(text, titulo_popup, mensaje_popup)

class QCForm(QMainWindow):
    def __init__(self, callback_generar=None):
        super().__init__()
        self.callback_generar = callback_generar
        self.setWindowTitle("QC Automatizado")
        self.setMinimumSize(900, 600) 
        
        # 🟢 Centramos la ventana vacía en la pantalla del usuario antes de mostrarla
        self._centrar_ventana()
        
        self.all_option_buttons = {}

        # 🟢 1. ESTADO DE CARGA SÚPER LIGERO
        # Mostramos un fondo oscuro y un cartel temporal casi sin gastar CPU/RAM
        self.setStyleSheet("QMainWindow { background-color: #1a1a1a; }")
        self.lbl_cargando = QLabel("Iniciando Motor Gráfico...", self)
        self.lbl_cargando.setStyleSheet("color: white; font-family: 'Segoe UI'; font-size: 16px; font-weight: bold;")
        self.lbl_cargando.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.lbl_cargando)

        # 🟢 2. DEJAMOS QUE LA VENTANA SE MUESTRE Y PATEAMOS LA CARGA
        # El QTimer espera 50ms para que la ventana se dibuje primero, y luego corre lo pesado
        QTimer.singleShot(50, self._iniciar_carga_diferida)

    def _centrar_ventana(self):
        """Calcula el centro de la pantalla actual y mueve la ventana ahí."""
        geometria_ventana = self.frameGeometry()
        centro_pantalla = self.screen().availableGeometry().center()
        geometria_ventana.moveCenter(centro_pantalla)
        self.move(geometria_ventana.topLeft())

    def _iniciar_carga_diferida(self):
        """Este método se ejecuta en segundo plano cuando la ventana vacía ya está en pantalla."""
        t_inicio_dibujo = time.perf_counter()
        
        # 3. Cargamos la imagen pesada, botones y sombras
        self._setup_icons()
        self._apply_stylesheet()
        self._build_ui() # Esto sobrescribe el lbl_cargando automáticamente
        
        self.btn_gen.setChecked(True)
        self.pages.setCurrentIndex(0)

        print(f">>> [PROFILER] Interfaz completa dibujada en: {time.perf_counter() - t_inicio_dibujo:.3f}s")

    def _setup_icons(self):
        ico_path = DIR_ASSETS / "logo_at.ico"
        if ico_path.exists(): self.setWindowIcon(QIcon(str(ico_path)))

    def _apply_stylesheet(self):
        bg_path = (DIR_ASSETS / "background.jpg").resolve().as_posix()
        blue_navy_solid = "#1A2865"
        glass_navy = "rgba(26, 40, 101, 140)" 
        glass_white = "rgba(255, 255, 255, 235)"
        blue_light = "#287bff"
        white = "#ffffff"
        dark = "#222222"

        self.setStyleSheet(f"""
            QMainWindow {{ border-image: url({bg_path}) 0 0 0 0 stretch stretch; background-color: #1a1a1a; }}
            QWidget#MainContainer {{ background-color: transparent; }}
            QFrame#DashboardFrame {{ background-color: transparent; }}
            
            QFrame#Sidebar {{ 
                background-color: {glass_navy};
                border-radius: 12px; 
                border: 1px solid rgba(255, 255, 255, 40);
            }}
            
            QFrame#ContentArea {{ 
                background-color: {glass_white}; 
                border-radius: 12px; 
                border: 1px solid rgba(0, 0, 0, 15);
            }}

            QLabel#BrandLabel {{ color: {white}; font-size: 18px; font-weight: bold; padding: 10px; }}
            
            QPushButton#SidebarButton {{
                background-color: transparent; color: {white}; text-align: left;
                padding-left: 15px; font-size: 13px; font-family: 'Segoe UI';
                border: 1px solid transparent; border-radius: 8px; margin: 2px 10px;
            }}
            QPushButton#SidebarButton:checked {{ 
                background-color: {white}; color: {blue_navy_solid}; font-weight: bold; 
                border: none;
            }}

            QLabel#PageTitle {{ color: {blue_navy_solid}; font-size: 20px; font-weight: bold; }}
            QLabel#SectionLabel {{ color: {dark}; font-size: 13px; font-weight: bold; margin-top: 5px; }}
            
            QLineEdit {{
                padding: 8px 10px; 
                border: 1px solid #d0d0d0; 
                border-radius: 6px;
                font-size: 12px; 
                background-color: {white};
                color: {dark}; 
            }}
            QLineEdit:focus {{ border: 2px solid {blue_light}; }}

            QToolButton#GridOptionButton {{
                background-color: {white}; 
                color: {blue_navy_solid}; 
                border: 1px solid #e0e0e0; 
                border-radius: 8px;
                font-size: 11px; 
                font-weight: bold;
            }}
            
            QToolButton#GridOptionButton:checked {{
                background-color: #f0f2f5; 
                border: 2px solid {blue_navy_solid};
            }}

            QPushButton#ActionButton {{
                background-color: {blue_navy_solid}; color: {white}; font-size: 13px; font-weight: bold;
                padding: 8px 20px; border-radius: 6px;
            }}
        """)

    def _build_ui(self):
        main_container = QWidget()
        main_container.setObjectName("MainContainer")
        self.setCentralWidget(main_container)
        
        main_layout = QVBoxLayout(main_container)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dashboard = QFrame()
        self.dashboard.setObjectName("DashboardFrame")
        self.dashboard.setFixedSize(680, 430) 
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.dashboard.setGraphicsEffect(shadow)

        dash_layout = QHBoxLayout(self.dashboard)
        dash_layout.setSpacing(15) 
        dash_layout.setContentsMargins(0, 0, 0, 0)

        # --- BARRA LATERAL ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(160) 
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 15, 0, 15)
        sidebar_layout.setSpacing(2)

        brand_label = QLabel("QC Auto")
        brand_label.setObjectName("BrandLabel")
        sidebar_layout.addWidget(brand_label)
        sidebar_layout.addSpacing(15)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_gen = LiquidSidebarButton("General", "🏠")
        self.btn_hw = LiquidSidebarButton("Hardware", "🖥️")
        self.btn_sw = LiquidSidebarButton("Software", "⚙️")
        self.btn_sellos = LiquidSidebarButton("Sellos", "🏷️")

        for i, btn in enumerate([self.btn_gen, self.btn_hw, self.btn_sw, self.btn_sellos]):
            sidebar_layout.addWidget(btn)
            self.nav_group.addButton(btn, i)

        sidebar_layout.addStretch()
        self.nav_group.idClicked.connect(self._on_nav_clicked)

        # --- ÁREA DE CONTENIDO ---
        content_area = QFrame()
        content_area.setObjectName("ContentArea")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)

        top_bar = QHBoxLayout()
        self.page_title = QLabel("General")
        self.page_title.setObjectName("PageTitle")
        top_bar.addWidget(self.page_title)
        top_bar.addStretch()
        content_layout.addLayout(top_bar)

        self.pages = QStackedWidget()
        self.page_gen = self._create_page_gen()
        
        self.page_hw = self._create_page_grid_options([
            ("Lectora DVD", "💿", "cd_dvd_rw"), ("Cable Poder", "🔌", "cable_de_poder"),
            ("HDMI", "📺", "hdmi"), ("Puerto RJ45", "🌐", "rj45"),
            ("Puertos USB", "🔌", "usb_ok"), 
            ("Teclado/Mouse", "⌨️", "teclado"), ("Webcam", "📷", "webcam")
        ])
        
        self.page_sw = self._create_page_grid_options([
            ("Windows Update", "🔄", "windows_update"), ("WiFi Funciona", "📶", "wifi")
        ])
        
        self.page_sellos = self._create_page_grid_options([
            ("AT Service", "🏷️", "sello_at_service"), ("Micro AMD/Intel", "🧠", "micro_intel_amd"),
            ("Sello Garantía", "✅", "sello_garantia"), ("COA Windows", "🪟", "coa_windows"),
            ("QC Rehecho", "🔄", "qc_rehecho")
        ])

        self.entry_codigo_at = QLineEdit()
        self.entry_codigo_at.setPlaceholderText("🔑 Ingresá el código de AT Service...")
        self.entry_codigo_at.setVisible(False)
        self.entry_codigo_at.setStyleSheet("margin-top: 10px;")
        
        grid_sellos = self.page_sellos.layout()
        grid_sellos.addWidget(self.entry_codigo_at, grid_sellos.rowCount(), 0, 1, 3)

        self.pages.addWidget(self.page_gen)
        self.pages.addWidget(self.page_hw)
        self.pages.addWidget(self.page_sw)
        self.pages.addWidget(self.page_sellos)

        scroll_content = QScrollArea()
        scroll_content.setWidgetResizable(True)
        scroll_content.setFrameShape(QFrame.Shape.NoFrame)
        scroll_content.setStyleSheet("background: transparent;")
        scroll_content.setWidget(self.pages)
        content_layout.addWidget(scroll_content)

        action_layout = QHBoxLayout()
        action_layout.addStretch()
        self.btn_submit = LiquidSubmitButton("Generar Reporte")
        self.btn_submit.clicked.connect(self._on_submit)
        action_layout.addWidget(self.btn_submit)
        content_layout.addLayout(action_layout)

        dash_layout.addWidget(self.sidebar)
        dash_layout.addWidget(content_area)
        main_layout.addWidget(self.dashboard)

        self.actualizar_ui_por_tipo_equipo()

    def _on_nav_clicked(self, id):
        self.pages.setCurrentIndex(id)
        titles = ["Vista General", "Hardware", "Software", "Sellos"]
        self.page_title.setText(titles[id])

    def _create_page_gen(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(QLabel("Tipo de Equipo", objectName="SectionLabel"))
        type_layout = QHBoxLayout()
        self.switch_equipo = InstagramPollSwitch()
        self.switch_equipo.installEventFilter(self)
        type_layout.addWidget(self.switch_equipo)
        type_layout.addStretch() 
        layout.addLayout(type_layout)
        layout.addSpacing(15)

        layout.addWidget(QLabel("Información", objectName="SectionLabel"))
        form_layout = QGridLayout()
        self.entry_qc = QLineEdit()
        self.entry_qc.setPlaceholderText("👤 Nombre del técnico...")
        form_layout.addWidget(self.entry_qc, 0, 0)
        self.entry_cliente = QLineEdit()
        self.entry_cliente.setPlaceholderText("🏢 Cliente...")
        form_layout.addWidget(self.entry_cliente, 1, 0)
        layout.addLayout(form_layout)
        return page

    def eventFilter(self, obj, event):
        if obj == self.switch_equipo and event.type() == QEvent.Type.MouseButtonRelease:
            QTimer.singleShot(50, self.actualizar_ui_por_tipo_equipo)
        return super().eventFilter(obj, event)

    def actualizar_ui_por_tipo_equipo(self):
        if hasattr(self, 'switch_equipo'):
            es_laptop = self.switch_equipo.is_laptop_selected()
            if "teclado" in self.all_option_buttons:
                self.all_option_buttons["teclado"].setVisible(es_laptop)
            if "webcam" in self.all_option_buttons:
                self.all_option_buttons["webcam"].setVisible(es_laptop)
            if "cable_de_poder" in self.all_option_buttons:
                self.all_option_buttons["cable_de_poder"].setText("Cargador" if es_laptop else "Cable Poder")

    def _create_page_grid_options(self, options):
        page = QWidget()
        grid_layout = QGridLayout(page)
        grid_layout.setSpacing(10) 
        grid_layout.setContentsMargins(0, 5, 0, 5)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        row, col, max_cols = 0, 0, 3 
        for text, icon, key in options:
            btn = LiquidGridButton(text, icon)
            btn.toggled.connect(lambda checked, k=key: self._handle_test_click(k, checked))
            grid_layout.addWidget(btn, row, col)
            self.all_option_buttons[key] = btn
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        return page

    def _handle_test_click(self, key, checked):
        if key == "sello_at_service":
            self.entry_codigo_at.setVisible(checked)
            if checked: self.entry_codigo_at.setFocus()
            else: self.entry_codigo_at.clear()
            return

        if not checked: return 

        # 🟢 LAZY LOADING: Las pruebas pesadas solo se importan acá,
        # en el milisegundo en el que el usuario hace clic.
        from src.pruebas import (
            HardwareTester, WebcamDialog, KeyboardTestDialog, 
            PowerListeningDialog, UsbTestDialog, HdmiListeningDialog, 
            Rj45ListeningDialog, WifiListeningDialog, WindowsUpdateDialog
        )

        success = False
        message = ""

        if key == "cable_de_poder":
            initial_check, _ = HardwareTester.test_power()
            if initial_check: success = True
            else:
                dlg = PowerListeningDialog(self); dlg.exec()
                success = dlg.success; message = "Se canceló la espera del cargador."
            if success: QMessageBox.information(self, "Hardware OK", "Funcionando correctamente.")

        elif key == "hdmi":
            # Eliminamos el escaneo previo, abrimos el diálogo directo
            dlg = HdmiListeningDialog(self)
            dlg.exec()
            success = dlg.success
            message = "Se canceló la espera del HDMI."
            if success: QMessageBox.information(self, "Hardware OK", "Monitor conectado y detectado.")
        
        elif key == "rj45":
            # Eliminamos el escaneo previo, abrimos el diálogo directo
            dlg = Rj45ListeningDialog(self)
            dlg.exec()
            success = dlg.success
            message = "Se canceló la espera de la red (RJ45)."
            if success: QMessageBox.information(self, "Hardware OK", "Cable de red RJ45 conectado y funcionando.")

        elif key == "webcam":
            if self.switch_equipo.is_laptop_selected():
                dlg = WebcamDialog(self); dlg.exec()
                success = dlg.result; message = "Cámara verificada" if success else "No se pudo validar la imagen"

        elif key == "usb_ok":
            dlg = UsbTestDialog(self); dlg.exec()
            success = dlg.success; message = "USB verificado" if success else "Cancelado"
            if success:
                self.cantidad_usb = dlg.total_ports  # 🟢 GUARDAMOS LA CANTIDAD REAL ACÁ

        elif key == "teclado":
            if self.switch_equipo.is_laptop_selected():
                dlg = KeyboardTestDialog(self); dlg.exec()
                success = dlg.tested_count > 0; message = "Teclado verificado"

        elif key == "windows_update":
            dlg = WindowsUpdateDialog(self); dlg.exec()
            success = dlg.success; message = "Cancelado"
            if success: QMessageBox.information(self, "Software OK", "Update verificado.")

        elif key == "wifi":
            dlg = WifiListeningDialog(self); dlg.exec()
            success = dlg.success; message = "Fallo WiFi"
            if success: QMessageBox.information(self, "Software OK", "WiFi OK.")

        if not success and message:
            QMessageBox.warning(self, "Error", message)
            self.all_option_buttons[key].setChecked(False)

    def _on_submit(self):
        tecnico = self.entry_qc.text().strip()
        cliente = self.entry_cliente.text().strip()
        if not tecnico or not cliente:
             QMessageBox.warning(self, "Incompleto", "Complete Técnico y Cliente.")
             return

        def get_checked(key):
            btn = self.all_option_buttons.get(key)
            return btn.isChecked() if btn else False

        codigo_at_val = None
        if get_checked("sello_at_service"):
            codigo_at_val = self.entry_codigo_at.text().strip()
            if not codigo_at_val:
                QMessageBox.warning(self, "Incompleto", "Ingresá el código AT Service.")
                return

        equipo = "LAP" if self.switch_equipo.is_laptop_selected() else "PC"
        hw_data = {
            "cd_dvd_rw": get_checked("cd_dvd_rw"), "cable_de_poder": get_checked("cable_de_poder"),
            "hdmi": get_checked("hdmi"), "rj45": get_checked("rj45"),
            "teclado": get_checked("teclado"), "webcam": get_checked("webcam")
        }
        sw_data = { "drivers": get_checked("windows_update"), "wifi": get_checked("wifi") }
        sellos_data = {
            "sello_at_service": get_checked("sello_at_service"), "micro_intel_amd": get_checked("micro_intel_amd"),
            "sello_garantia": get_checked("sello_garantia"), "coa_windows": get_checked("coa_windows"),
            "qc_rehecho": get_checked("qc_rehecho"),
        }
        
        # 🟢 Agarramos la cantidad testeada, o pasamos 0 si no lo testearon
        cantidad_usb = getattr(self, 'cantidad_usb', 0) 
        
        datos = DatosFormulario(
            equipo=equipo, 
            realizado_por=tecnico, 
            cliente=cliente, 
            usb=cantidad_usb, 
            hw=hw_data, 
            sw=sw_data, 
            sellos=sellos_data, 
            codigo_at=codigo_at_val
        )
        if self.callback_generar:
            self.callback_generar(datos)
            self.close()

def manejador_errores(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
        sys.__excepthook__(exc_type, exc_value, exc_traceback); return
    error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    with open("crash_log.txt", "a", encoding="utf-8") as f: f.write(error_details + "\n")
    msg = QMessageBox(); msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText("Error fatal. Revisar crash_log.txt"); msg.setDetailedText(error_details); msg.exec()

def lanzar_interfaz(callback_generar=None):
    app = QApplication(sys.argv)
    sys.excepthook = manejador_errores 
    app.setFont(QFont("Segoe UI", 10))
    window = QCForm(callback_generar)
    window.show() # Ventana salta inmediatamente (ahora en el centro de la pantalla)
    sys.exit(app.exec())