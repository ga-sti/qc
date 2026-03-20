# src/pruebas.py
import psutil
import cv2
import subprocess
import win32api
import win32con
from PyQt6.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QGridLayout, QFrame
)
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QMouseEvent, QWheelEvent, QFont, QGuiApplication
from PyQt6.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal

class HardwareTester:
    @staticmethod
    def test_power():
        battery = psutil.sensors_battery()
        if battery is None:
            return True, "PC de escritorio detectada (Alimentación AC)."
        if battery.power_plugged:
            return True, "Cargador detectado correctamente."
        return False, "Por favor, conecta el cargador para continuar."

    @staticmethod
    def test_hdmi() -> tuple[bool, str]:
        """
        Consulta infalible al Administrador de Dispositivos vía PowerShell.
        """
        try:
            comando = 'powershell -NoProfile -Command "@(Get-PnpDevice -Class Monitor -PresentOnly).Count"'
            out = subprocess.check_output(comando, shell=True, creationflags=0x08000000, text=True).strip()
            cantidad = int(out)
            if cantidad > 1:
                return True, f"Monitor externo detectado ({cantidad})."
        except Exception:
            pass
        return False, "Esperando monitor externo..."
    
    @staticmethod
    def test_rj45():
        """
        Consulta infalible vía PowerShell para adaptadores físicos de red (Ethernet).
        """
        try:
            comando = "powershell -NoProfile -Command \"@(Get-NetAdapter -Physical | Where-Object { $_.InterfaceType -eq 6 -and $_.Status -eq 'Up' }).Count\""
            out = subprocess.check_output(comando, shell=True, creationflags=0x08000000, text=True).strip()
            cantidad = int(out)
            if cantidad > 0:
                return True, f"Conexión de red RJ45 detectada ({cantidad} activas)."
        except Exception:
            pass
        return False, "Conecta un cable RJ-45 activo al puerto."


class WebcamDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prueba de Cámara")
        self.setFixedSize(450, 420)
        self.setStyleSheet("background-color: white; border-radius: 12px;")
        
        self._centrar_ventana() # 🟢 CENTRADO AUTOMÁTICO
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.img_label = QLabel("Iniciando cámara...")
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setFixedSize(400, 300)
        self.img_label.setStyleSheet("background: #000; color: white; border-radius: 10px; margin-bottom: 10px;")
        layout.addWidget(self.img_label)

        self.question_lbl = QLabel("¿La imagen se ve nítida y fluida?")
        self.question_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #1A2865; margin-bottom: 5px;")
        layout.addWidget(self.question_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.btn_no = QPushButton("❌ No (Falla)")
        self.btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_no.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 10px; font-weight: bold; border-radius: 8px; font-size: 13px;} QPushButton:hover { background-color: #d32f2f; }")
        self.btn_no.clicked.connect(self.rechazar_imagen)
        
        self.btn_yes = QPushButton("✅ Sí (Aprobar)")
        self.btn_yes.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_yes.setStyleSheet("QPushButton { background-color: #4caf50; color: white; padding: 10px; font-weight: bold; border-radius: 8px; font-size: 13px;} QPushButton:hover { background-color: #388e3c; }")
        self.btn_yes.clicked.connect(self.aprobar_imagen)

        btn_layout.addWidget(self.btn_no)
        btn_layout.addWidget(self.btn_yes)
        layout.addLayout(btn_layout)

        self.result = False
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            self.img_label.setText("⚠️ No se detectó ninguna cámara web.")
            self.btn_yes.setEnabled(False)
            self.btn_yes.setStyleSheet("background-color: #9e9e9e; color: white; padding: 10px; font-weight: bold; border-radius: 8px;")
        else:
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)

    def _centrar_ventana(self):
        geometria = self.frameGeometry()
        centro = self.screen().availableGeometry().center()
        geometria.moveCenter(centro)
        self.move(geometria.topLeft())

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            img = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
            self.img_label.setPixmap(QPixmap.fromImage(img).scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio))

    def aprobar_imagen(self):
        self.result = True
        self.cerrar_camara()
        self.accept()

    def rechazar_imagen(self):
        self.result = False
        self.cerrar_camara()
        self.accept()

    def cerrar_camara(self):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

    def closeEvent(self, event):
        self.cerrar_camara()
        super().closeEvent(event)


class KeyboardTestDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Test Integral de Teclado y Mouse")
        self.setFixedSize(900, 500) 
        self.setStyleSheet("background-color: #f5f5f5;")
        
        self._centrar_ventana() # 🟢 CENTRADO AUTOMÁTICO
        
        main_layout = QVBoxLayout(self)
        self.keys_labels = {}
        self.mouse_labels = {}
        self.tested_count = 0
        
        keyboard_frame = QFrame()
        keyboard_layout = QGridLayout(keyboard_frame)
        keyboard_layout.setSpacing(5)
        
        layout_keys = [
            [("Esc", Qt.Key.Key_Escape), ("F1", Qt.Key.Key_F1), ("F2", Qt.Key.Key_F2), ("F3", Qt.Key.Key_F3), ("F4", Qt.Key.Key_F4), ("F5", Qt.Key.Key_F5), ("F6", Qt.Key.Key_F6), ("F7", Qt.Key.Key_F7), ("F8", Qt.Key.Key_F8), ("F9", Qt.Key.Key_F9), ("F10", Qt.Key.Key_F10), ("F11", Qt.Key.Key_F11), ("F12", Qt.Key.Key_F12)],
            [("1", Qt.Key.Key_1), ("2", Qt.Key.Key_2), ("3", Qt.Key.Key_3), ("4", Qt.Key.Key_4), ("5", Qt.Key.Key_5), ("6", Qt.Key.Key_6), ("7", Qt.Key.Key_7), ("8", Qt.Key.Key_8), ("9", Qt.Key.Key_9), ("0", Qt.Key.Key_0), ("'", Qt.Key.Key_Apostrophe), ("¿", Qt.Key.Key_Question), ("Backspace", Qt.Key.Key_Backspace)],
            [("Tab", Qt.Key.Key_Tab), ("Q", Qt.Key.Key_Q), ("W", Qt.Key.Key_W), ("E", Qt.Key.Key_E), ("R", Qt.Key.Key_R), ("T", Qt.Key.Key_T), ("Y", Qt.Key.Key_Y), ("U", Qt.Key.Key_U), ("I", Qt.Key.Key_I), ("O", Qt.Key.Key_O), ("P", Qt.Key.Key_P), ("Enter", Qt.Key.Key_Return)],
            [("Caps", Qt.Key.Key_CapsLock), ("A", Qt.Key.Key_A), ("S", Qt.Key.Key_S), ("D", Qt.Key.Key_D), ("F", Qt.Key.Key_F), ("G", Qt.Key.Key_G), ("H", Qt.Key.Key_H), ("J", Qt.Key.Key_J), ("K", Qt.Key.Key_K), ("L", Qt.Key.Key_L), ("Ñ", Qt.Key.Key_Ntilde), ("+", Qt.Key.Key_Plus)],
            [("Shift", Qt.Key.Key_Shift), ("Z", Qt.Key.Key_Z), ("X", Qt.Key.Key_X), ("C", Qt.Key.Key_C), ("V", Qt.Key.Key_V), ("B", Qt.Key.Key_B), ("N", Qt.Key.Key_N), ("M", Qt.Key.Key_M), (",", Qt.Key.Key_Comma), (".", Qt.Key.Key_Period), ("-", Qt.Key.Key_Minus), ("Up", Qt.Key.Key_Up)],
            [("Ctrl", Qt.Key.Key_Control), ("Win", Qt.Key.Key_Meta), ("Alt", Qt.Key.Key_Alt), ("Space", Qt.Key.Key_Space), ("AltGr", Qt.Key.Key_AltGr), ("Left", Qt.Key.Key_Left), ("Down", Qt.Key.Key_Down), ("Right", Qt.Key.Key_Right)]
        ]

        for row_idx, row in enumerate(layout_keys):
            col_idx = 0
            for text, key_code in row:
                lbl = QLabel(text)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                if text == "Space": lbl.setFixedSize(250, 40)
                elif text in ["Enter", "Backspace", "Shift", "Caps"]: lbl.setFixedSize(90, 40)
                else: lbl.setFixedSize(50, 40)

                lbl.setStyleSheet("border: 2px solid #d0d0d0; border-radius: 6px; background: white; color: #1A2865; font-weight: bold;")
                
                col_span = 5 if text == "Space" else (2 if text in ["Enter", "Backspace", "Shift", "Caps"] else 1)
                keyboard_layout.addWidget(lbl, row_idx, col_idx, 1, col_span)
                
                self.keys_labels[key_code] = lbl
                col_idx += col_span
                
        main_layout.addWidget(keyboard_frame)

        mouse_layout = QHBoxLayout()
        mouse_title = QLabel("🖱️ Test de Mouse (Clickea y scrollea por acá):")
        mouse_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1A2865;")
        mouse_layout.addWidget(mouse_title)

        mouse_btns = [("Izquierdo", "Left"), ("Rueda (Clic)", "Middle"), ("Derecho", "Right"), ("Scroll Arriba", "ScrollUp"), ("Scroll Abajo", "ScrollDown")]
        
        for text, key in mouse_btns:
            lbl = QLabel(text)
            lbl.setFixedSize(110, 40)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("border: 2px solid #d0d0d0; border-radius: 6px; background: white; color: #1A2865; font-weight: bold;")
            mouse_layout.addWidget(lbl)
            self.mouse_labels[key] = lbl
            
        mouse_layout.addStretch()
        main_layout.addLayout(mouse_layout)

        self.btn_done = QPushButton("Finalizar Test")
        self.btn_done.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_done.setStyleSheet("QPushButton { background: #1A2865; color: white; padding: 12px; font-weight: bold; font-size: 14px; border-radius: 8px; margin-top: 15px; } QPushButton:hover { background: #287bff; }")
        self.btn_done.clicked.connect(self.accept)
        main_layout.addWidget(self.btn_done)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _centrar_ventana(self):
        geometria = self.frameGeometry()
        centro = self.screen().availableGeometry().center()
        geometria.moveCenter(centro)
        self.move(geometria.topLeft())

    def mark_success(self, widget: QLabel):
        widget.setStyleSheet("background: #4caf50; color: white; border: 2px solid #2e7d32; font-weight: bold;")
        self.tested_count += 1

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in self.keys_labels:
            self.mark_success(self.keys_labels[key])
            
        if event.nativeVirtualKey() == 165 or key == Qt.Key.Key_AltGr:
            if Qt.Key.Key_AltGr in self.keys_labels:
                self.mark_success(self.keys_labels[Qt.Key.Key_AltGr])
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mark_success(self.mouse_labels["Left"])
        elif event.button() == Qt.MouseButton.RightButton:
            self.mark_success(self.mouse_labels["Right"])
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.mark_success(self.mouse_labels["Middle"])
        super().mousePressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        angle = event.angleDelta().y()
        if angle > 0:
            self.mark_success(self.mouse_labels["ScrollUp"])
        elif angle < 0:
            self.mark_success(self.mouse_labels["ScrollDown"])
        super().wheelEvent(event)


class PowerListeningDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Escucha Activa - Alimentación")
        self.setFixedSize(350, 180)
        self.setStyleSheet("background-color: white; border-radius: 12px;")
        
        self._centrar_ventana() # 🟢 CENTRADO AUTOMÁTICO
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_lbl = QLabel("🔌")
        self.icon_lbl.setFont(QFont("Segoe UI", 30))
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_lbl)

        self.msg_lbl = QLabel("Esperando conexión de cargador...")
        self.msg_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #1A2865;")
        self.msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.msg_lbl)

        self.sub_msg = QLabel("Enchufá el cable para continuar automáticamente")
        self.sub_msg.setStyleSheet("color: #666; font-size: 11px;")
        self.sub_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_msg)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_status)
        self.timer.start(500)

        self.success = False

    def _centrar_ventana(self):
        geometria = self.frameGeometry()
        centro = self.screen().availableGeometry().center()
        geometria.moveCenter(centro)
        self.move(geometria.topLeft())

    def check_status(self):
        battery = psutil.sensors_battery()
        if battery is None or battery.power_plugged:
            self.success = True
            self.timer.stop()
            self.msg_lbl.setText("¡Cargador Detectado!")
            self.msg_lbl.setStyleSheet("color: #4caf50; font-size: 16px; font-weight: bold;")
            self.icon_lbl.setText("⚡")
            self.sub_msg.setText("Continuando automáticamente...")
            QTimer.singleShot(1000, self.accept)

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)


# =======================================================
# NUEVOS DIÁLOGOS DE ESCUCHA ACTIVA (HDMI y RJ45) - CON HILOS
# =======================================================

class HdmiScannerThread(QThread):
    result_ready = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        while self.running:
            conectado, _ = HardwareTester.test_hdmi()
            if conectado:
                self.result_ready.emit(True)
                self.running = False
            self.msleep(1500) # Duerme el hilo, no la interfaz

    def stop(self):
        self.running = False
        self.wait()

class Rj45ScannerThread(QThread):
    result_ready = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        while self.running:
            conectado, _ = HardwareTester.test_rj45()
            if conectado:
                self.result_ready.emit(True)
                self.running = False
            self.msleep(1500)

    def stop(self):
        self.running = False
        self.wait()

class HdmiListeningDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Escucha Activa - HDMI")
        self.setFixedSize(350, 180)
        self.setStyleSheet("background-color: white; border-radius: 12px;")
        
        self._centrar_ventana() # 🟢 CENTRADO AUTOMÁTICO
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_lbl = QLabel("📺")
        self.icon_lbl.setFont(QFont("Segoe UI", 30))
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_lbl)

        self.msg_lbl = QLabel("Esperando monitor externo...")
        self.msg_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #1A2865;")
        self.msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.msg_lbl)

        self.sub_msg = QLabel("Conectá el cable HDMI/DisplayPort para continuar")
        self.sub_msg.setStyleSheet("color: #666; font-size: 11px;")
        self.sub_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_msg)

        self.success = False

        # 🟢 Arranca el hilo en segundo plano (No congela)
        self.scanner = HdmiScannerThread()
        self.scanner.result_ready.connect(self.on_scan_success)
        self.scanner.start()

    def _centrar_ventana(self):
        geometria = self.frameGeometry()
        centro = self.screen().availableGeometry().center()
        geometria.moveCenter(centro)
        self.move(geometria.topLeft())

    def on_scan_success(self, conectado):
        if conectado:
            self.success = True
            self.msg_lbl.setText("¡Monitor Detectado!")
            self.msg_lbl.setStyleSheet("color: #4caf50; font-size: 16px; font-weight: bold;")
            self.icon_lbl.setText("✅")
            self.sub_msg.setText("Continuando automáticamente...")
            QTimer.singleShot(1500, self.accept)

    def closeEvent(self, event):
        self.scanner.stop()
        super().closeEvent(event)


class Rj45ListeningDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Escucha Activa - Red RJ45")
        self.setFixedSize(350, 180)
        self.setStyleSheet("background-color: white; border-radius: 12px;")
        
        self._centrar_ventana() # 🟢 CENTRADO AUTOMÁTICO
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_lbl = QLabel("🌐")
        self.icon_lbl.setFont(QFont("Segoe UI", 30))
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_lbl)

        self.msg_lbl = QLabel("Esperando cable de red...")
        self.msg_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #1A2865;")
        self.msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.msg_lbl)

        self.sub_msg = QLabel("Conectá un cable LAN con internet para continuar")
        self.sub_msg.setStyleSheet("color: #666; font-size: 11px;")
        self.sub_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_msg)

        self.success = False

        # 🟢 Arranca el hilo en segundo plano (No congela)
        self.scanner = Rj45ScannerThread()
        self.scanner.result_ready.connect(self.on_scan_success)
        self.scanner.start()

    def _centrar_ventana(self):
        geometria = self.frameGeometry()
        centro = self.screen().availableGeometry().center()
        geometria.moveCenter(centro)
        self.move(geometria.topLeft())

    def on_scan_success(self, conectado):
        if conectado:
            self.success = True
            self.msg_lbl.setText("¡Red Detectada!")
            self.msg_lbl.setStyleSheet("color: #4caf50; font-size: 16px; font-weight: bold;")
            self.icon_lbl.setText("✅")
            self.sub_msg.setText("Continuando automáticamente...")
            QTimer.singleShot(1500, self.accept)

    def closeEvent(self, event):
        self.scanner.stop()
        super().closeEvent(event)


# =======================================================
# HILOS DE ESCANEO AVANZADO (USB Y WINDOWS UPDATE)
# =======================================================

class UsbScannerThread(QThread):
    devices_updated = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        while self.running:
            try:
                out = subprocess.check_output(
                    ["pnputil", "/enum-devices", "/connected"],
                    creationflags=0x08000000, text=True
                )
                count = out.count("USB\\VID_")
            except Exception:
                try:
                    out = subprocess.check_output(
                        ["wmic", "path", "Win32_PnPEntity", "where", "Present='true'", "get", "PNPDeviceID"],
                        creationflags=0x08000000, text=True
                    )
                    count = out.count("USB\\VID_")
                except Exception:
                    count = 0
            
            self.devices_updated.emit(count)
            self.msleep(500)

    def stop(self):
        self.running = False
        self.wait()


class UsbTestDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Test de Puertos USB")
        self.setFixedSize(450, 350)
        self.setStyleSheet("background-color: white; border-radius: 12px;")
        
        self._centrar_ventana() # 🟢 CENTRADO AUTOMÁTICO
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.total_ports = 0
        self.tested_ports = 0
        self.baseline_count = 0
        self.plugged_count = 0
        self.state = "ASK_QTY"
        self.success = False

        self._build_ui_ask_qty()

        self.scanner_thread = UsbScannerThread()
        self.scanner_thread.devices_updated.connect(self._on_scan_result)

    def _centrar_ventana(self):
        geometria = self.frameGeometry()
        centro = self.screen().availableGeometry().center()
        geometria.moveCenter(centro)
        self.move(geometria.topLeft())

    def get_initial_pendrives(self):
        try:
            out = subprocess.check_output(
                ["wmic", "logicaldisk", "where", "drivetype=2", "get", "Name"],
                creationflags=0x08000000, text=True
            )
            return len([line for line in out.splitlines() if ":" in line])
        except Exception:
            return 0

    def _build_ui_ask_qty(self):
        self._clear_layout()
        lbl_title = QLabel("🔌 Test de Puertos USB")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1A2865;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(lbl_title)

        lbl_desc = QLabel("¿Cuántos puertos físicos vas a testear?")
        lbl_desc.setStyleSheet("font-size: 13px; color: #333;")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(lbl_desc)

        grid = QGridLayout()
        grid.setSpacing(10)
        for i in range(1, 7):
            btn = QPushButton(str(i))
            btn.setFixedSize(60, 50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("QPushButton { background-color: #f0f2f5; color: #1A2865; font-size: 16px; font-weight: bold; border: 2px solid #d0d0d0; border-radius: 8px; } QPushButton:hover { background-color: #e0e0e0; border: 2px solid #1A2865; }")
            btn.clicked.connect(lambda checked, val=i: self.start_test(val))
            row, col = divmod(i-1, 3)
            grid.addWidget(btn, row, col)
        self.main_layout.addLayout(grid)

    def _build_ui_testing(self):
        self._clear_layout()
        self.lbl_status_icon = QLabel("⏳")
        self.lbl_status_icon.setFont(QFont("Segoe UI", 40))
        self.lbl_status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.lbl_status_icon)

        self.lbl_status_text = QLabel("Preparando escaneo seguro...")
        self.lbl_status_text.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A2865;")
        self.lbl_status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.lbl_status_text)

        self.lbl_counter = QLabel(f"Puertos probados: {self.tested_ports} / {self.total_ports}")
        self.lbl_counter.setStyleSheet("font-size: 14px; color: #666; margin-top: 10px;")
        self.lbl_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.lbl_counter)

    def _clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget(): sub.widget().deleteLater()
                item.layout().deleteLater()

    def start_test(self, qty):
        self.total_ports = qty
        self._build_ui_testing()
        self.state = "WAIT_BASELINE"
        self.scanner_thread.start()

    def update_ui_state(self):
        self.lbl_counter.setText(f"Puertos probados: {self.tested_ports} / {self.total_ports}")
        if self.state == "WAIT_PLUG":
            self.lbl_status_icon.setText("⬇️")
            self.lbl_status_text.setText(f"Conectá un USB\nen el puerto {self.tested_ports + 1}...")
        elif self.state == "WAIT_UNPLUG":
            self.lbl_status_icon.setText("⬆️")
            self.lbl_status_text.setText("¡Detectado!\nAhora desconectalo.")

    def _on_scan_result(self, current_count):
        if self.state == "WAIT_BASELINE":
            self.baseline_count = current_count
            pendrives_iniciales = self.get_initial_pendrives()
            if pendrives_iniciales > 0:
                self.tested_ports = min(pendrives_iniciales, self.total_ports)
                self.plugged_count = current_count
                if self.tested_ports >= self.total_ports: self.finish_success()
                else:
                    self.state = "WAIT_UNPLUG"
                    self.update_ui_state()
            else:
                self.state = "WAIT_PLUG"
                self.update_ui_state()

        elif self.state == "WAIT_PLUG":
            if current_count > self.baseline_count:
                self.tested_ports += 1
                self.plugged_count = current_count
                if self.tested_ports >= self.total_ports: self.finish_success()
                else:
                    self.state = "WAIT_UNPLUG"
                    self.update_ui_state()
            elif current_count < self.baseline_count:
                self.baseline_count = current_count

        elif self.state == "WAIT_UNPLUG":
            if current_count < self.plugged_count:
                self.baseline_count = current_count
                self.state = "WAIT_PLUG"
                self.update_ui_state()

    def finish_success(self):
        self.scanner_thread.stop()
        self.success = True
        self.lbl_status_icon.setText("✅")
        self.lbl_status_text.setText("¡Todos los puertos verificados!")
        self.lbl_status_text.setStyleSheet("font-size: 16px; font-weight: bold; color: #4caf50;")
        self.lbl_counter.setText(f"Puertos probados: {self.total_ports} / {self.total_ports}")
        QTimer.singleShot(1500, self.accept)

    def closeEvent(self, event):
        self.scanner_thread.stop()
        super().closeEvent(event)


class WifiListeningDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prueba de Wi-Fi")
        self.setFixedSize(350, 220)
        self.setStyleSheet("background-color: white; border-radius: 12px;")
        
        self._centrar_ventana() # 🟢 CENTRADO AUTOMÁTICO
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_lbl = QLabel("📶")
        self.icon_lbl.setFont(QFont("Segoe UI", 30))
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_lbl)

        self.msg_lbl = QLabel("Esperando conexión Wi-Fi...")
        self.msg_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #1A2865;")
        self.msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.msg_lbl)

        self.sub_msg = QLabel("Conectate a una red desde el panel que se abrirá.")
        self.sub_msg.setStyleSheet("color: #666; font-size: 11px;")
        self.sub_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_msg)

        self.btn_open = QPushButton("Abrir Redes Wi-Fi")
        self.btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open.setStyleSheet("QPushButton { background-color: #f0f2f5; color: #1A2865; border: 1px solid #d0d0d0; padding: 8px; border-radius: 6px; font-weight: bold;} QPushButton:hover { background-color: #e0e0e0; }")
        self.btn_open.clicked.connect(self.open_wifi_panel)
        layout.addWidget(self.btn_open)

        self.success = False
        QTimer.singleShot(500, self.open_wifi_panel)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_status)
        self.timer.start(1500)

    def _centrar_ventana(self):
        geometria = self.frameGeometry()
        centro = self.screen().availableGeometry().center()
        geometria.moveCenter(centro)
        self.move(geometria.topLeft())

    def open_wifi_panel(self):
        try:
            subprocess.Popen("start ms-availablenetworks:", shell=True)
        except:
            pass

    def check_status(self):
        try:
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                creationflags=0x08000000, text=True
            )
            if " connected" in out or " conectado" in out:
                self.success = True
                self.timer.stop()
                self.msg_lbl.setText("¡Wi-Fi Conectado!")
                self.msg_lbl.setStyleSheet("color: #4caf50; font-size: 14px; font-weight: bold;")
                self.icon_lbl.setText("✅")
                self.sub_msg.hide()
                self.btn_open.hide()
                QTimer.singleShot(1500, self.accept)
        except Exception:
            pass

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)


class WUScannerThread(QThread):
    result_ready = pyqtSignal(int)

    def run(self):
        ps_script = (
            "$UpdateSession = New-Object -ComObject Microsoft.Update.Session; "
            "$UpdateSearcher = $UpdateSession.CreateUpdateSearcher(); "
            "$UpdateSearcher.Online = $false; "
            "$SearchResult = $UpdateSearcher.Search('IsInstalled=0 and Type=''Software'' and IsHidden=0'); "
            "Write-Output $SearchResult.Updates.Count"
        )
        try:
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", ps_script],
                creationflags=0x08000000, text=True, timeout=15
            )
            count = int(out.strip())
        except Exception:
            count = -1
        self.result_ready.emit(count)


class WindowsUpdateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Test de Windows Update")
        self.setFixedSize(380, 220)
        self.setStyleSheet("background-color: white; border-radius: 12px;")
        
        self._centrar_ventana() # 🟢 CENTRADO AUTOMÁTICO
        
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_lbl = QLabel("⏳")
        self.icon_lbl.setFont(QFont("Segoe UI", 30))
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.icon_lbl)

        self.msg_lbl = QLabel("Verificando actualizaciones...")
        self.msg_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #1A2865;")
        self.msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.msg_lbl)

        self.sub_msg = QLabel("Consultando la base de datos de Windows...\nEsto tomará unos segundos.")
        self.sub_msg.setStyleSheet("color: #666; font-size: 12px;")
        self.sub_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.sub_msg)

        self.btn_layout = QHBoxLayout()
        
        self.btn_no = QPushButton("❌ Cancelar")
        self.btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_no.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 10px; font-weight: bold; border-radius: 8px; font-size: 13px;} QPushButton:hover { background-color: #d32f2f; }")
        self.btn_no.clicked.connect(self.reject)
        self.btn_no.hide()

        self.btn_yes = QPushButton("✅ Todo Actualizado")
        self.btn_yes.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_yes.setStyleSheet("QPushButton { background-color: #4caf50; color: white; padding: 10px; font-weight: bold; border-radius: 8px; font-size: 13px;} QPushButton:hover { background-color: #388e3c; }")
        self.btn_yes.clicked.connect(self.mark_success)
        self.btn_yes.hide()

        self.btn_layout.addWidget(self.btn_no)
        self.btn_layout.addWidget(self.btn_yes)
        self.layout.addLayout(self.btn_layout)

        self.success = False

        self.scanner = WUScannerThread()
        self.scanner.result_ready.connect(self.on_scan_complete)
        self.scanner.start()

    def _centrar_ventana(self):
        geometria = self.frameGeometry()
        centro = self.screen().availableGeometry().center()
        geometria.moveCenter(centro)
        self.move(geometria.topLeft())

    def on_scan_complete(self, count):
        if count == 0:
            self.icon_lbl.setText("✅")
            self.msg_lbl.setText("¡Sistema al día!")
            self.msg_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #4caf50;")
            self.sub_msg.setText("No hay actualizaciones pendientes.")
            self.success = True
            QTimer.singleShot(1500, self.accept)
        else:
            self.icon_lbl.setText("🔄")
            if count > 0: self.msg_lbl.setText(f"Hay {count} actualización(es) pendiente(s)")
            else: self.msg_lbl.setText("Validación manual requerida")
            self.sub_msg.setText("Abriendo Windows Update...\nInstalá las actualizaciones y confirmá abajo.")
            self.btn_no.show()
            self.btn_yes.show()
            self.open_update()

    def open_update(self):
        try:
            subprocess.Popen("start ms-settings:windowsupdate-action", shell=True)
        except Exception:
            pass

    def mark_success(self):
        self.success = True
        self.accept()