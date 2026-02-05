from PyQt6.QtWidgets import (
    QLabel, QFrame, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QProgressBar, QWidget, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QScrollArea, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QThread, QSize, QUrl, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QColor, QPixmap, QIcon, QImage, QFontMetrics, QPainter
from src.utils.logger import logger
from PIL import Image, ImageQt

class ElidedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setMinimumWidth(50) # Ensure it has some width

    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.TextElideMode.ElideMiddle, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)

class ThumbnailLoader(QThread):
    thumbnail_ready = pyqtSignal(str, QImage) # file_path, qimage

    def __init__(self):
        super().__init__()
        self.queue = []
        self.running = True
        self.cache = {}

    def add_task(self, file_path):
        if file_path not in self.cache:
            self.queue.append(file_path)
            if not self.isRunning():
                self.start()

    def run(self):
        while self.running and self.queue:
            file_path = self.queue.pop(0)
            try:
                # Create thumbnail using Pillow for high quality
                img = Image.open(file_path)
                
                # Center crop to square
                width, height = img.size
                min_dim = min(width, height)
                left = (width - min_dim) / 2
                top = (height - min_dim) / 2
                right = (width + min_dim) / 2
                bottom = (height + min_dim) / 2
                
                img = img.crop((left, top, right, bottom))
                img.thumbnail((120, 120), Image.Resampling.LANCZOS)
                
                # Convert to QImage (Thread Safe)
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                
                # Create QImage from PIL image data
                # Using ImageQt directly can be buggy with garbage collection, 
                # safer to create a copy
                qim = ImageQt.ImageQt(img)
                qimage = qim.copy()
                
                self.cache[file_path] = qimage
                self.thumbnail_ready.emit(file_path, qimage)
                
            except Exception as e:
                logger.error(f"Failed to generate thumbnail for {file_path}: {e}")
            
            # Small sleep to prevent freezing UI
            self.msleep(10)

    def stop(self):
        self.running = False
        self.wait()

class ModernButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)
        self._anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _animate_to(self, value):
        if self._anim.state() == QPropertyAnimation.State.Running:
            self._anim.stop()
        self._anim.setStartValue(self._opacity_effect.opacity())
        self._anim.setEndValue(value)
        self._anim.start()

    def enterEvent(self, event):
        self._animate_to(0.94)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(1.0)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._animate_to(0.9)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._animate_to(0.94 if self.underMouse() else 1.0)
        super().mouseReleaseEvent(event)

class ModernCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.content_layout = QHBoxLayout(self)
        self.content_layout.setContentsMargins(12, 8, 12, 8)
        self.content_layout.setSpacing(8)

class ImageListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setIconSize(QSize(120, 120))
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setGridSize(QSize(140, 160))
        # Default to Free movement to allow drag/drop if enabled
        self.setMovement(QListWidget.Movement.Free)
        self.setSpacing(10)
        
        self.loader = ThumbnailLoader()
        self.loader.thumbnail_ready.connect(self.update_thumbnail)
        
    def add_image(self, file_path):
        import os
        name = os.path.basename(file_path)
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Unchecked)
        # Set placeholder icon initially
        item.setIcon(QIcon(file_path)) 
        
        self.addItem(item)
        self.loader.add_task(file_path)

    def get_checked_items(self):
        items = []
        for i in range(self.count()):
            item = self.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                items.append(item)
        return items

    def set_all_check_state(self, state: Qt.CheckState):
        for i in range(self.count()):
            self.item(i).setCheckState(state)

    def get_all_items(self):
        items = []
        for i in range(self.count()):
            items.append(self.item(i))
        return items

    def update_thumbnail(self, file_path, qimage):
        # Find items with this file_path
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == file_path:
                # Convert QImage to QPixmap/QIcon in Main Thread (Safe)
                pixmap = QPixmap.fromImage(qimage)
                item.setIcon(QIcon(pixmap))
                break

class DropZone(QLabel):
    files_dropped = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setObjectName("DropZone")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("\n\n拖拽图片或文件夹到此处\n\n")
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            files.append(file_path)
        
        if files:
            self.files_dropped.emit(files)

class TaskTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["选择", "文件名", "任务类型", "状态", "进度"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(0, 50)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(3, 100)
        self.setColumnWidth(4, 150)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Allow checking the checkbox but no text editing
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def add_task(self, filename, task_type):
        row = self.rowCount()
        self.insertRow(row)
        
        # Checkbox item
        check_item = QTableWidgetItem()
        check_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        check_item.setCheckState(Qt.CheckState.Unchecked)
        self.setItem(row, 0, check_item)
        
        self.setItem(row, 1, QTableWidgetItem(filename))
        self.setItem(row, 2, QTableWidgetItem(task_type))
        self.setItem(row, 3, QTableWidgetItem("等待中"))
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(False)
        self.setCellWidget(row, 4, progress_bar)
        
        return row

    def update_status(self, row, status, color=None):
        item = self.item(row, 3)
        item.setText(status)
        if color:
            item.setForeground(QColor(color))

    def update_progress(self, row, value):
        widget = self.cellWidget(row, 4)
        if isinstance(widget, QProgressBar):
            widget.setValue(value)

    def get_checked_rows(self):
        rows = []
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item.checkState() == Qt.CheckState.Checked:
                rows.append(row)
        return rows
    
    def set_all_check_state(self, state: Qt.CheckState):
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            item.setCheckState(state)
            
    def remove_rows(self, rows):
        # Sort in reverse order to avoid index shifting issues
        for row in sorted(rows, reverse=True):
            self.removeRow(row)

class InteractivePreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar for controls
        self.toolbar = QHBoxLayout()
        self.btn_zoom_in = ModernButton("+")
        self.btn_zoom_out = ModernButton("-")
        self.btn_fit = ModernButton("适应")
        
        self.btn_zoom_in.setObjectName("ToolButton")
        self.btn_zoom_out.setObjectName("ToolButton")
        self.btn_fit.setObjectName("ToolButton")
        
        self.btn_zoom_in.setFixedWidth(40)
        self.btn_zoom_out.setFixedWidth(40)
        self.btn_fit.setFixedWidth(60)
        
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        self.btn_fit.clicked.connect(self.fit_to_window)
        
        self.toolbar.addWidget(QLabel("预览操作:"))
        self.toolbar.addStretch()
        self.toolbar.addWidget(self.btn_zoom_out)
        self.toolbar.addWidget(self.btn_fit)
        self.toolbar.addWidget(self.btn_zoom_in)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.image_label = QLabel("暂无预览")
        self.image_label.setObjectName("PreviewCanvas")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.scroll_area.setWidget(self.image_label)
        
        self.layout.addLayout(self.toolbar)
        self.layout.addWidget(self.scroll_area)
        
        self.pixmap = None
        self.scale_factor = 1.0
        
    def set_image(self, pixmap):
        self.pixmap = pixmap
        self.scale_factor = 1.0
        self.fit_to_window()
        
    def update_display(self):
        if self.pixmap:
            if self.scale_factor <= 0:
                self.scale_factor = 0.1
                
            scaled_w = int(self.pixmap.width() * self.scale_factor)
            scaled_h = int(self.pixmap.height() * self.scale_factor)
            
            self.image_label.setPixmap(self.pixmap.scaled(
                scaled_w, scaled_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            self.image_label.resize(scaled_w, scaled_h)
            
    def zoom_in(self):
        self.scale_factor *= 1.2
        self.update_display()
        
    def zoom_out(self):
        self.scale_factor *= 0.8
        self.update_display()
        
    def fit_to_window(self):
        if not self.pixmap:
            return
            
        # Calculate scale to fit
        view_w = self.scroll_area.viewport().width()
        view_h = self.scroll_area.viewport().height()
        
        img_w = self.pixmap.width()
        img_h = self.pixmap.height()
        
        if img_w == 0 or img_h == 0:
            return
            
        scale_w = view_w / img_w
        scale_h = view_h / img_h
        
        self.scale_factor = min(scale_w, scale_h) * 0.95 # Leave some margin
        self.update_display()

class PreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("预览区域")
        self.label.setObjectName("PreviewLabel")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setMinimumHeight(200)
        layout.addWidget(self.label)
        self.setLayout(layout)
    
    def set_image(self, pixmap):
        self.label.setPixmap(pixmap.scaled(
            self.label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))
