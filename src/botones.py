# src/botones.py
from PyQt6.QtWidgets import QPushButton, QToolButton, QSizePolicy, QWidget
from PyQt6.QtGui import QPainter, QRadialGradient, QColor, QCursor, QBrush, QFont, QIcon, QPen
from PyQt6.QtCore import Qt, QPoint, QVariantAnimation, QRectF, pyqtProperty, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize

class LiquidEffectMixin:
    """Mixin para efectos de brillo interactivo y ondas de agua (Ripple)."""
    def init_liquid(self):
        self.setMouseTracking(True) 
        self._mouse_pos = QPoint(-1, -1)
        self._is_hovered = False
        self._ripple_pos = QPoint(0, 0)
        self._ripple_radius = 0.0
        self._ripple_opacity = 0
        
        # Animación de la expansión de la onda
        self.anim_radius = QVariantAnimation(self)
        self.anim_radius.setDuration(400) 
        self.anim_radius.setStartValue(0.0)
        self.anim_radius.setEndValue(150.0)
        self.anim_radius.valueChanged.connect(self._update_radius)
        
        # Animación del desvanecimiento
        self.anim_opacity = QVariantAnimation(self)
        self.anim_opacity.setDuration(400)
        self.anim_opacity.setStartValue(100) # Opacidad inicial para visibilidad
        self.anim_opacity.setEndValue(0)
        self.anim_opacity.valueChanged.connect(self._update_opacity)

    def _update_radius(self, value):
        self._ripple_radius = float(value)
        self.update()

    def _update_opacity(self, value):
        self._ripple_opacity = value
        self.update()

    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        if hasattr(super(), 'enterEvent'): super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        if hasattr(super(), 'leaveEvent'): super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        self._mouse_pos = event.pos()
        self.update() 
        if hasattr(super(), 'mouseMoveEvent'): super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        self._ripple_pos = event.pos()
        self.anim_radius.start()
        self.anim_opacity.start()
        if hasattr(super(), 'mousePressEvent'): super().mousePressEvent(event)

    def draw_liquid_effects(self, painter, is_checked=False, effect_color=QColor(255, 255, 255)):
        """Dibuja el brillo especular y la onda expansiva con el color indicado."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Brillo de seguimiento (Hover)
        if self._is_hovered and not is_checked:
            grad = QRadialGradient(float(self._mouse_pos.x()), float(self._mouse_pos.y()), 60.0)
            c_center = QColor(effect_color)
            c_center.setAlpha(40)
            c_edge = QColor(effect_color)
            c_edge.setAlpha(0)  
            grad.setColorAt(0, c_center) 
            grad.setColorAt(1, c_edge)  
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(self.rect(), 8, 8)

        # 2. Onda de agua (Click)
        if self._ripple_opacity > 0:
            ripple_c = QColor(effect_color)
            ripple_c.setAlpha(self._ripple_opacity)
            painter.setBrush(ripple_c)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setClipRect(self.rect()) 
            rect = QRectF(
                float(self._ripple_pos.x()) - self._ripple_radius,
                float(self._ripple_pos.y()) - self._ripple_radius,
                self._ripple_radius * 2.0,
                self._ripple_radius * 2.0
            )
            painter.drawEllipse(rect)

# ==========================================
# COMPONENTES VISUALES
# ==========================================

class LiquidSidebarButton(LiquidEffectMixin, QPushButton):
    """Botón para el menú lateral (Texto blanco sobre azul marino)."""
    def __init__(self, text, icon_text, parent=None):
        super().__init__(parent)
        self.init_liquid()
        self.setCheckable(True)
        self.setText(f" {icon_text}  {text}")
        self.setFixedHeight(40)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setObjectName("SidebarButton")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event):
        super().paintEvent(event) 
        painter = QPainter(self)
        # Brillo blanco para el fondo oscuro
        self.draw_liquid_effects(painter, self.isChecked(), QColor(255, 255, 255)) 
        painter.end()

class LiquidGridButton(LiquidEffectMixin, QToolButton):
    """Tarjetas de Hardware/Software (Letras azul marino sobre fondo claro)."""
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(parent)
        self.init_liquid()
        self.setCheckable(True)
        self.setText(text)
        self.navy_color = QColor("#1A2865")
        
        # Soporte para iconos personalizados PNG
        if icon_path:
            self.setIcon(QIcon(str(icon_path)))
            self.setIconSize(QSize(32, 32))
            
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setFixedSize(115, 85)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setObjectName("GridOptionButton")
        
        # Forzar color de texto para evitar que se ponga blanco al clickear
        self.setStyleSheet(f"color: {self.navy_color.name()}; font-weight: bold; border: none;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fondo y bordes según estado (Regla de selección suave)
        if self.isChecked():
            painter.setBrush(QColor("#f0f2f5")) # Gris muy claro
            painter.setPen(QPen(self.navy_color, 1.5)) # Borde Navy fino
            painter.drawRoundedRect(self.rect().adjusted(1,1,-1,-1), 8, 8)
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor("#e0e0e0"), 1)) # Borde gris tenue
            painter.drawRoundedRect(self.rect().adjusted(1,1,-1,-1), 8, 8)
        painter.end()
        
        super().paintEvent(event)
        
        painter = QPainter(self)
        # Efecto azul marino para que resalte sobre el blanco
        self.draw_liquid_effects(painter, self.isChecked(), self.navy_color)
        painter.end()

class LiquidSubmitButton(LiquidEffectMixin, QPushButton):
    """Botón de acción principal."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.init_liquid()
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setObjectName("ActionButton")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        self.draw_liquid_effects(painter, False, QColor(255, 255, 255))
        painter.end()

class InstagramPollSwitch(QWidget):
    """Interruptor rectangular (8px radius) animado estilo encuesta."""
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(240, 40)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        self._is_laptop = False 
        self._anim_progress = 0.0 

        self.animation = QPropertyAnimation(self, b"anim_progress")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad) 
        self.animation.setDuration(300)

        self.font_label = QFont("Segoe UI", 11, QFont.Weight.Bold)
        self.color_navy = QColor(26, 40, 101, 230) # #1A2865
        self.color_white = QColor("#ffffff")
        self.color_text_inactive = QColor(255, 255, 255, 170) 

    @pyqtProperty(float)
    def anim_progress(self):
        return self._anim_progress

    @anim_progress.setter
    def anim_progress(self, value):
        self._anim_progress = value
        self.update()

    def is_laptop_selected(self):
        return self._is_laptop

    def mousePressEvent(self, event):
        self._is_laptop = not self._is_laptop
        self.toggled.emit(self._is_laptop)
        
        self.animation.stop()
        self.animation.setEndValue(1.0 if self._is_laptop else 0.0)
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self.font_label)
        
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        slider_width = width / 2
        radius = 8 # Bordes menos redondos según lo solicitado

        # Fondo principal
        painter.setBrush(QBrush(self.color_navy))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        # Pastilla deslizante blanca
        current_slider_x = self._anim_progress * (width - slider_width)
        slider_rect = QRectF(current_slider_x, 0, slider_width, height)
        slider_rect_adjusted = slider_rect.adjusted(3, 3, -3, -3) 
        
        painter.setBrush(QBrush(self.color_white))
        painter.drawRoundedRect(slider_rect_adjusted, radius - 2, radius - 2)

        # Textos con cambio de color dinámico
        rect_pc = QRectF(0, 0, slider_width, height)
        rect_lap = QRectF(width / 2, 0, slider_width, height)

        # Colores contrastados
        color_pc = self.color_navy if not self._is_laptop else self.color_text_inactive
        color_lap = self.color_navy if self._is_laptop else self.color_text_inactive

        painter.setPen(color_pc)
        painter.drawText(rect_pc, Qt.AlignmentFlag.AlignCenter, "🖥️ PC")

        painter.setPen(color_lap)
        painter.drawText(rect_lap, Qt.AlignmentFlag.AlignCenter, "💻 Laptop")

        painter.end()# src/botones.py
from PyQt6.QtWidgets import QPushButton, QToolButton, QSizePolicy, QWidget
from PyQt6.QtGui import QPainter, QRadialGradient, QColor, QCursor, QBrush, QFont, QIcon, QPen
from PyQt6.QtCore import Qt, QPoint, QVariantAnimation, QRectF, pyqtProperty, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize

class LiquidEffectMixin:
    """Mixin para efectos de brillo interactivo y ondas de agua (Ripple)."""
    def init_liquid(self):
        self.setMouseTracking(True) 
        self._mouse_pos = QPoint(-1, -1)
        self._is_hovered = False
        self._ripple_pos = QPoint(0, 0)
        self._ripple_radius = 0.0
        self._ripple_opacity = 0
        
        # Animación de la expansión de la onda
        self.anim_radius = QVariantAnimation(self)
        self.anim_radius.setDuration(400) 
        self.anim_radius.setStartValue(0.0)
        self.anim_radius.setEndValue(150.0)
        self.anim_radius.valueChanged.connect(self._update_radius)
        
        # Animación del desvanecimiento
        self.anim_opacity = QVariantAnimation(self)
        self.anim_opacity.setDuration(400)
        self.anim_opacity.setStartValue(100) # Opacidad inicial para visibilidad
        self.anim_opacity.setEndValue(0)
        self.anim_opacity.valueChanged.connect(self._update_opacity)

    def _update_radius(self, value):
        self._ripple_radius = float(value)
        self.update()

    def _update_opacity(self, value):
        self._ripple_opacity = value
        self.update()

    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        if hasattr(super(), 'enterEvent'): super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        if hasattr(super(), 'leaveEvent'): super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        self._mouse_pos = event.pos()
        self.update() 
        if hasattr(super(), 'mouseMoveEvent'): super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        self._ripple_pos = event.pos()
        self.anim_radius.start()
        self.anim_opacity.start()
        if hasattr(super(), 'mousePressEvent'): super().mousePressEvent(event)

    def draw_liquid_effects(self, painter, is_checked=False, effect_color=QColor(255, 255, 255)):
        """Dibuja el brillo especular y la onda expansiva con el color indicado."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Brillo de seguimiento (Hover)
        if self._is_hovered and not is_checked:
            grad = QRadialGradient(float(self._mouse_pos.x()), float(self._mouse_pos.y()), 60.0)
            c_center = QColor(effect_color)
            c_center.setAlpha(40)
            c_edge = QColor(effect_color)
            c_edge.setAlpha(0)  
            grad.setColorAt(0, c_center) 
            grad.setColorAt(1, c_edge)  
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(self.rect(), 8, 8)

        # 2. Onda de agua (Click)
        if self._ripple_opacity > 0:
            ripple_c = QColor(effect_color)
            ripple_c.setAlpha(self._ripple_opacity)
            painter.setBrush(ripple_c)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setClipRect(self.rect()) 
            rect = QRectF(
                float(self._ripple_pos.x()) - self._ripple_radius,
                float(self._ripple_pos.y()) - self._ripple_radius,
                self._ripple_radius * 2.0,
                self._ripple_radius * 2.0
            )
            painter.drawEllipse(rect)

# ==========================================
# COMPONENTES VISUALES
# ==========================================

class LiquidSidebarButton(LiquidEffectMixin, QPushButton):
    """Botón para el menú lateral (Texto blanco sobre azul marino)."""
    def __init__(self, text, icon_text, parent=None):
        super().__init__(parent)
        self.init_liquid()
        self.setCheckable(True)
        self.setText(f" {icon_text}  {text}")
        self.setFixedHeight(40)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setObjectName("SidebarButton")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event):
        super().paintEvent(event) 
        painter = QPainter(self)
        # Brillo blanco para el fondo oscuro
        self.draw_liquid_effects(painter, self.isChecked(), QColor(255, 255, 255)) 
        painter.end()

class LiquidGridButton(LiquidEffectMixin, QToolButton):
    """Tarjetas de Hardware/Software (Letras azul marino sobre fondo claro)."""
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(parent)
        self.init_liquid()
        self.setCheckable(True)
        self.setText(text)
        self.navy_color = QColor("#1A2865")
        
        # Soporte para iconos personalizados PNG
        if icon_path:
            self.setIcon(QIcon(str(icon_path)))
            self.setIconSize(QSize(32, 32))
            
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setFixedSize(115, 85)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setObjectName("GridOptionButton")
        
        # Forzar color de texto para evitar que se ponga blanco al clickear
        self.setStyleSheet(f"color: {self.navy_color.name()}; font-weight: bold; border: none;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fondo y bordes según estado (Regla de selección suave)
        if self.isChecked():
            painter.setBrush(QColor("#f0f2f5")) # Gris muy claro
            painter.setPen(QPen(self.navy_color, 1.5)) # Borde Navy fino
            painter.drawRoundedRect(self.rect().adjusted(1,1,-1,-1), 8, 8)
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor("#e0e0e0"), 1)) # Borde gris tenue
            painter.drawRoundedRect(self.rect().adjusted(1,1,-1,-1), 8, 8)
        painter.end()
        
        super().paintEvent(event)
        
        painter = QPainter(self)
        # Efecto azul marino para que resalte sobre el blanco
        self.draw_liquid_effects(painter, self.isChecked(), self.navy_color)
        painter.end()

class LiquidSubmitButton(LiquidEffectMixin, QPushButton):
    """Botón de acción principal."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.init_liquid()
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setObjectName("ActionButton")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        self.draw_liquid_effects(painter, False, QColor(255, 255, 255))
        painter.end()

class InstagramPollSwitch(QWidget):
    """Interruptor rectangular (8px radius) animado estilo encuesta."""
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(240, 40)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        self._is_laptop = False 
        self._anim_progress = 0.0 

        self.animation = QPropertyAnimation(self, b"anim_progress")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad) 
        self.animation.setDuration(300)

        self.font_label = QFont("Segoe UI", 11, QFont.Weight.Bold)
        self.color_navy = QColor(26, 40, 101, 230) # #1A2865
        self.color_white = QColor("#ffffff")
        self.color_text_inactive = QColor(255, 255, 255, 170) 

    @pyqtProperty(float)
    def anim_progress(self):
        return self._anim_progress

    @anim_progress.setter
    def anim_progress(self, value):
        self._anim_progress = value
        self.update()

    def is_laptop_selected(self):
        return self._is_laptop

    def mousePressEvent(self, event):
        self._is_laptop = not self._is_laptop
        self.toggled.emit(self._is_laptop)
        
        self.animation.stop()
        self.animation.setEndValue(1.0 if self._is_laptop else 0.0)
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self.font_label)
        
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        slider_width = width / 2
        radius = 8 # Bordes menos redondos según lo solicitado

        # Fondo principal
        painter.setBrush(QBrush(self.color_navy))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        # Pastilla deslizante blanca
        current_slider_x = self._anim_progress * (width - slider_width)
        slider_rect = QRectF(current_slider_x, 0, slider_width, height)
        slider_rect_adjusted = slider_rect.adjusted(3, 3, -3, -3) 
        
        painter.setBrush(QBrush(self.color_white))
        painter.drawRoundedRect(slider_rect_adjusted, radius - 2, radius - 2)

        # Textos con cambio de color dinámico
        rect_pc = QRectF(0, 0, slider_width, height)
        rect_lap = QRectF(width / 2, 0, slider_width, height)

        # Colores contrastados
        color_pc = self.color_navy if not self._is_laptop else self.color_text_inactive
        color_lap = self.color_navy if self._is_laptop else self.color_text_inactive

        painter.setPen(color_pc)
        painter.drawText(rect_pc, Qt.AlignmentFlag.AlignCenter, "🖥️ PC")

        painter.setPen(color_lap)
        painter.drawText(rect_lap, Qt.AlignmentFlag.AlignCenter, "💻 Laptop")

        painter.end()