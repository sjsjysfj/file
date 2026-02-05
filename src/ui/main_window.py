import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QFileDialog, QLabel, QComboBox, QGroupBox, QListWidget,
    QAbstractItemView, QMessageBox, QSplitter, QCheckBox, QDialog, QProgressBar,
    QSpinBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QThreadPool, QSize, QUrl, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QDesktopServices, QImage
from PIL import Image, ImageQt

from src.ui.widgets import DropZone, ImageListWidget, PreviewWidget, InteractivePreviewWidget, ModernButton, ModernCard, ElidedLabel
from src.core.processor import ImageProcessor
from src.core.worker import Worker
from src.utils.logger import logger
from src.ui.theme import get_stylesheet

class StitchPreviewWorker(QThread):
    result_ready = pyqtSignal(object) # QImage or None
    
    def __init__(self, images, mode, max_width=300):
        super().__init__()
        self.images = images
        self.mode = mode
        self.max_width = max_width
        self._is_cancelled = False
        
    def run(self):
        try:
            if self._is_cancelled: return
            # Call processor static method
            pil_img = ImageProcessor.generate_stitch_preview(self.images, self.mode, self.max_width)
            
            if self._is_cancelled: return
            
            if pil_img:
                # Convert to QImage (Thread Safe)
                if pil_img.mode != "RGBA":
                    pil_img = pil_img.convert("RGBA")
                    
                qim = ImageQt.ImageQt(pil_img)
                qimage = qim.copy()
                
                self.result_ready.emit(qimage)
            else:
                self.result_ready.emit(None)
        except Exception as e:
            logger.error(f"Preview worker error: {e}")
            self.result_ready.emit(None)
            
    def cancel(self):
        self._is_cancelled = True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图像处理专家")
        self.resize(1200, 800)
        
        self.is_dark_mode = False
        
        self.threadpool = QThreadPool()
        logger.info(f"Multithreading with maximum {self.threadpool.maxThreadCount()} threads")

        self.init_ui()
        self.apply_theme() # Apply initial theme
        
        # Connect tab change signal
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Initial visibility check
        self.on_tab_changed(0)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_bar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        top_bar.setMaximumHeight(50)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(16, 0, 16, 0)
        top_bar_layout.setSpacing(12)

        self.lbl_title = QLabel("图像处理工作台")
        self.lbl_title.setObjectName("AppTitle")
        self.lbl_subtitle = QLabel("全能图像分割与拼接工具")
        self.lbl_subtitle.setObjectName("AppSubtitle")
        
        top_bar_layout.addWidget(self.lbl_title)
        top_bar_layout.addWidget(self.lbl_subtitle)

        self.btn_theme_toggle = ModernButton("🌙 深色模式")
        self.btn_theme_toggle.setObjectName("GhostButton")
        self.btn_theme_toggle.setCheckable(True)
        self.btn_theme_toggle.clicked.connect(self.toggle_theme)

        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.btn_theme_toggle)

        main_layout.addWidget(top_bar)

        settings_panel = QFrame()
        settings_panel.setObjectName("SidePanel")
        settings_panel.setMinimumWidth(260)
        settings_panel.setMaximumWidth(360)
        settings_layout = QVBoxLayout(settings_panel)
        settings_layout.setContentsMargins(16, 16, 16, 16)
        settings_layout.setSpacing(12)

        settings_title = QLabel("设置")
        settings_title.setObjectName("SectionTitle")
        settings_layout.addWidget(settings_title)
        
        # Output Directory
        self.output_dir_label = ElidedLabel("输出目录: (默认源目录)")
        self.output_dir_label.setObjectName("Caption")
        # self.output_dir_label.setWordWrap(True) # Removed in favor of ElidedLabel
        self.btn_select_output = ModernButton("选择输出目录")
        self.btn_select_output.clicked.connect(self.select_output_dir)
        
        # Output Format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["保持原格式", "JPG", "PNG", "BMP"])
        
        # Stitch Mode
        self.stitch_mode_label = QLabel("拼接模式:")
        self.stitch_mode_label.setObjectName("Caption")
        self.stitch_mode_combo = QComboBox()
        self.stitch_mode_combo.addItems(["等宽缩放", "中心裁剪", "填充背景"])
        self.stitch_mode_combo.currentTextChanged.connect(self.update_stitch_preview)
        
        # New Options
        self.chk_create_subfolder = QCheckBox("为每张图创建独立文件夹")
        self.chk_create_subfolder.setChecked(False)
        self.chk_create_subfolder.setToolTip("在输出目录下以原文件名创建子文件夹存放分割后的图片")
        
        self.chk_auto_open = QCheckBox("处理完成后打开文件夹")
        self.chk_auto_open.setChecked(False)
        
        format_label = QLabel("输出格式:")
        format_label.setObjectName("Caption")
        settings_layout.addWidget(format_label)
        settings_layout.addWidget(self.format_combo)
        settings_layout.addWidget(self.stitch_mode_label)
        settings_layout.addWidget(self.stitch_mode_combo)
        settings_layout.addWidget(self.output_dir_label)
        settings_layout.addWidget(self.btn_select_output)
        settings_layout.addWidget(self.chk_create_subfolder)
        settings_layout.addWidget(self.chk_auto_open)
        settings_layout.addStretch()
        
        self.btn_process = ModernButton("开始处理")
        self.btn_process.setObjectName("PrimaryButton")
        self.btn_process.clicked.connect(self.start_processing)
        settings_layout.addWidget(self.btn_process)

        content_panel = QFrame()
        content_panel.setObjectName("ContentPanel")
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(12)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)
        
        # Tab 1: Split
        self.split_tab = QWidget()
        self.split_tab.setObjectName("Surface")
        self.split_layout = QVBoxLayout(self.split_tab)
        self.split_layout.setContentsMargins(16, 24, 16, 16)
        self.split_layout.setSpacing(12)
        
        split_toolbar = QHBoxLayout()
        split_toolbar.setSpacing(8)
        
        self.btn_import_split = ModernButton("导入文件...")
        self.btn_import_split.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
        self.btn_import_split.clicked.connect(self.import_split_files)
        
        param_group = ModernCard()
        param_layout = param_group.content_layout

        param_title = QLabel("分割参数")
        param_title.setObjectName("Caption")
        param_layout.addWidget(param_title)
        
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(1, 10)
        self.spin_rows.setValue(2)
        self.spin_rows.setSuffix(" 行")
        self.spin_rows.valueChanged.connect(self.validate_split_params)
        
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(1, 10)
        self.spin_cols.setValue(2)
        self.spin_cols.setSuffix(" 列")
        self.spin_cols.valueChanged.connect(self.validate_split_params)
        
        param_layout.addWidget(QLabel("横向:"))
        param_layout.addWidget(self.spin_cols)
        param_layout.addWidget(QLabel("纵向:"))
        param_layout.addWidget(self.spin_rows)
        
        self.btn_select_all = ModernButton("全选")
        self.btn_select_all.clicked.connect(lambda: self.split_list.set_all_check_state(Qt.CheckState.Checked))
        
        self.btn_select_none = ModernButton("反选")
        self.btn_select_none.clicked.connect(lambda: self.invert_selection())
        
        self.btn_remove_selected = ModernButton("删除选中")
        self.btn_remove_selected.clicked.connect(self.remove_selected_tasks)
        
        split_toolbar.addWidget(self.btn_import_split)
        split_toolbar.addWidget(param_group)
        split_toolbar.addStretch()
        split_toolbar.addWidget(self.btn_select_all)
        split_toolbar.addWidget(self.btn_select_none)
        split_toolbar.addWidget(self.btn_remove_selected)
        
        self.split_drop = DropZone()
        self.split_drop.files_dropped.connect(self.add_split_files)
        self.split_drop.setMaximumHeight(100)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.split_list = ImageListWidget()
        self.split_list.currentItemChanged.connect(self.on_split_item_changed)
        
        self.preview_widget = PreviewWidget()
        
        self.splitter.addWidget(self.split_list)
        self.splitter.addWidget(self.preview_widget)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        
        self.split_layout.addLayout(split_toolbar)
        self.split_layout.addWidget(self.split_drop)
        self.split_layout.addWidget(self.splitter)
        
        # Tab 2: Stitch
        self.stitch_tab = QWidget()
        self.stitch_tab.setObjectName("Surface")
        
        # Main Horizontal Layout for Stitch Tab
        self.stitch_root_layout = QHBoxLayout(self.stitch_tab)
        self.stitch_root_layout.setContentsMargins(16, 16, 16, 16)
        self.stitch_root_layout.setSpacing(12)
        
        # Left Column: Tools + List
        self.stitch_left_panel = QWidget()
        self.stitch_left_layout = QVBoxLayout(self.stitch_left_panel)
        self.stitch_left_layout.setContentsMargins(0, 0, 0, 0)
        self.stitch_left_layout.setSpacing(12)
        
        stitch_toolbar = QHBoxLayout()
        stitch_toolbar.setSpacing(8)
        
        self.btn_import_stitch = ModernButton("导入图片...")
        self.btn_import_stitch.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
        self.btn_import_stitch.clicked.connect(self.import_stitch_files)
        
        self.btn_import_folder_stitch = ModernButton("导入文件夹...")
        self.btn_import_folder_stitch.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DirIcon))
        self.btn_import_folder_stitch.clicked.connect(self.import_stitch_folder)
        
        self.btn_clear_stitch = ModernButton("清空列表")
        self.btn_clear_stitch.clicked.connect(lambda: [self.stitch_list.clear(), self.update_stitch_preview()])
        
        self.btn_preview_stitch = ModernButton("刷新预览")
        self.btn_preview_stitch.clicked.connect(self.update_stitch_preview)
        
        self.combo_preview_quality = QComboBox()
        self.combo_preview_quality.addItems(["预览: 低 (快)", "预览: 中", "预览: 高 (慢)"])
        self.combo_preview_quality.currentIndexChanged.connect(self.update_stitch_preview)
        
        stitch_toolbar.addWidget(self.btn_import_stitch)
        stitch_toolbar.addWidget(self.btn_import_folder_stitch)
        drag_hint = QLabel("拖拽调整顺序")
        drag_hint.setObjectName("Caption")
        stitch_toolbar.addWidget(drag_hint)
        stitch_toolbar.addStretch()
        
        # Second Toolbar Row for Actions (to save width)
        stitch_actions_toolbar = QHBoxLayout()
        stitch_actions_toolbar.setSpacing(8)
        stitch_actions_toolbar.addWidget(self.combo_preview_quality)
        stitch_actions_toolbar.addWidget(self.btn_preview_stitch)
        stitch_actions_toolbar.addWidget(self.btn_clear_stitch)
        
        self.stitch_drop = DropZone()
        self.stitch_drop.files_dropped.connect(self.add_stitch_files)
        self.stitch_drop.setMaximumHeight(80)
        
        self.stitch_list = ImageListWidget() 
        self.stitch_list.setViewMode(QListWidget.ViewMode.ListMode)
        self.stitch_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.stitch_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.stitch_list.model().rowsMoved.connect(self.update_stitch_preview)
        
        self.stitch_left_layout.addLayout(stitch_toolbar)
        self.stitch_left_layout.addLayout(stitch_actions_toolbar)
        self.stitch_left_layout.addWidget(self.stitch_drop)
        self.stitch_left_layout.addWidget(self.stitch_list)
        
        # Right Column: Preview
        self.stitch_preview = InteractivePreviewWidget()
        
        # Add to Splitter
        self.stitch_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.stitch_splitter.addWidget(self.stitch_left_panel)
        self.stitch_splitter.addWidget(self.stitch_preview)
        self.stitch_splitter.setStretchFactor(0, 1)
        self.stitch_splitter.setStretchFactor(1, 2)
        
        self.stitch_root_layout.addWidget(self.stitch_splitter)
        
        self.tabs.addTab(self.split_tab, "图片分割")
        self.tabs.addTab(self.stitch_tab, "图片拼接")
        
        content_layout.addWidget(self.tabs)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.addWidget(settings_panel)
        self.main_splitter.addWidget(content_panel)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setSizes([300, 900])

        main_layout.addWidget(self.main_splitter)

        self.output_dir = None
        # self.split_tasks removed, using list items directly
        
        # Tracking active tasks for auto-open
        self.active_tasks_count = 0
        self.last_output_dir = None
        self.preview_worker = None

    def toggle_theme(self):
        self.is_dark_mode = self.btn_theme_toggle.isChecked()
        self.btn_theme_toggle.setText("☀️ 浅色模式" if self.is_dark_mode else "🌙 深色模式")
        self.apply_theme()
        
    def apply_theme(self):
        qss = get_stylesheet(self.is_dark_mode)
        self.setStyleSheet(qss)

    def resizeEvent(self, event):
        width = self.width()
        if width < 980:
            self.main_splitter.setOrientation(Qt.Orientation.Vertical)
            self.main_splitter.setSizes([260, max(400, self.height() - 260)])
        else:
            self.main_splitter.setOrientation(Qt.Orientation.Horizontal)
        super().resizeEvent(event)

    def on_tab_changed(self, index):
        # 0 is Split Tab
        is_split = (index == 0)
        self.chk_create_subfolder.setVisible(is_split)
        
        # Update stitch mode visibility
        self.stitch_mode_combo.setVisible(not is_split)
        self.stitch_mode_label.setVisible(not is_split)

    def validate_split_params(self):
        # QSpinBox prevents invalid numbers, but we can double check
        rows = self.spin_rows.value()
        cols = self.spin_cols.value()
        
        # Logic: If for some reason value is 0 (shouldn't happen with setRange), disable
        if rows < 1 or cols < 1:
            self.btn_process.setEnabled(False)
            self.spin_rows.setStyleSheet("border: 1px solid red;")
        else:
            self.btn_process.setEnabled(True)
            self.spin_rows.setStyleSheet("")
            self.spin_cols.setStyleSheet("")

    def invert_selection(self):
        for i in range(self.split_list.count()):
            item = self.split_list.item(i)
            new_state = Qt.CheckState.Unchecked if item.checkState() == Qt.CheckState.Checked else Qt.CheckState.Checked
            item.setCheckState(new_state)

    def remove_selected_tasks(self):
        items = self.split_list.get_checked_items()
        for item in items:
            row = self.split_list.row(item)
            self.split_list.takeItem(row)
        # Also clear preview if current item removed
        if self.split_list.count() == 0:
            self.preview_widget.label.setText("预览区域")
            self.preview_widget.label.setPixmap(QPixmap())

    def import_split_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "导入图片", 
            "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if files:
            self.add_split_files(files)

    def select_output_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if d:
            self.output_dir = d
            self.output_dir_label.setText(f"输出目录:\n{d}")

    def add_split_files(self, files):
        for f in files:
            if os.path.isfile(f):
                if not f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    continue
                self.split_list.add_image(f)
            elif os.path.isdir(f):
                for root, _, filenames in os.walk(f):
                    for name in filenames:
                        if name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                            full_path = os.path.join(root, name)
                            self.split_list.add_image(full_path)
    
    def on_split_item_changed(self, current, previous):
        if not current:
            return
        
        file_path = current.data(Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            try:
                pixmap = QPixmap(file_path)
                self.preview_widget.set_image(pixmap)
            except Exception as e:
                logger.error(f"Failed to load preview for {file_path}: {e}")

    def import_stitch_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "导入图片", 
            "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if files:
            self.add_stitch_files(files)

    def import_stitch_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "导入文件夹")
        if folder:
            self.add_stitch_files([folder])

    def add_stitch_files(self, files):
        added = False
        for f in files:
            if os.path.isfile(f) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self.stitch_list.add_image(f)
                added = True
            elif os.path.isdir(f):
                 for root, _, filenames in os.walk(f):
                    for name in filenames:
                        if name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                            self.stitch_list.add_image(os.path.join(root, name))
                            added = True
        if added:
            self.update_stitch_preview()

    def update_stitch_preview(self):
        # Cancel previous worker if running
        if self.preview_worker and self.preview_worker.isRunning():
            self.preview_worker.cancel()
            self.preview_worker.wait()
            
        items = self.stitch_list.get_all_items()
        if not items:
            self.stitch_preview.set_image(QPixmap())
            return
            
        images = [item.data(Qt.ItemDataRole.UserRole) for item in items]
        if not images:
            return
            
        mode_map = {
            "等宽缩放": "resize",
            "中心裁剪": "crop",
            "填充背景": "fill"
        }
        mode = mode_map.get(self.stitch_mode_combo.currentText(), "resize")
        
        # Determine quality/size
        quality_idx = self.combo_preview_quality.currentIndex()
        max_width = 300
        if quality_idx == 1: max_width = 600
        elif quality_idx == 2: max_width = 1000
        
        self.stitch_preview.image_label.setText("正在生成预览...")
        
        self.preview_worker = StitchPreviewWorker(images, mode, max_width)
        self.preview_worker.result_ready.connect(self.on_preview_ready)
        self.preview_worker.start()
        
    def on_preview_ready(self, qimage):
        if qimage:
            # Convert QImage to QPixmap in Main Thread (Safe)
            pixmap = QPixmap.fromImage(qimage)
            self.stitch_preview.set_image(pixmap)
        else:
            self.stitch_preview.image_label.setText("预览失败")

    def start_processing(self):
        # Validation: Check output directory
        if not self.output_dir:
            QMessageBox.warning(self, "提示", "请先选择输出目录！")
            self.select_output_dir()
            if not self.output_dir:
                return
                
        if not os.path.exists(self.output_dir):
             try:
                 os.makedirs(self.output_dir)
             except Exception:
                 QMessageBox.warning(self, "提示", "所选输出目录不存在且无法创建！")
                 return

        current_idx = self.tabs.currentIndex()
        
        out_fmt = self.format_combo.currentText()
        if out_fmt == "保持原格式":
            out_fmt = None
        else:
            out_fmt = out_fmt.lower()

        if current_idx == 0: # Split
            self.process_split_tasks(out_fmt)
        else: # Stitch
            self.process_stitch_task(out_fmt)

    def process_split_tasks(self, out_fmt):
        checked_items = self.split_list.get_checked_items()
        
        # If no items checked, process ALL items? 
        # Requirement usually implies if selection exists, process selection. 
        # If nothing selected (checked), maybe process all?
        # Let's follow previous logic: if checked_rows, process them. Else process all.
        
        items_to_process = checked_items if checked_items else [self.split_list.item(i) for i in range(self.split_list.count())]

        if not items_to_process:
            QMessageBox.information(self, "提示", "没有待处理的任务")
            return

        self.active_tasks_count = len(items_to_process)
        self.last_output_dir = None # Reset
        
        rows = self.spin_rows.value()
        cols = self.spin_cols.value()

        for item in items_to_process:
            filepath = item.data(Qt.ItemDataRole.UserRole)
            
            # Update status (visual indication)
            item.setText(f"{os.path.basename(filepath)} (处理中...)")
            item.setForeground(Qt.GlobalColor.blue)
            
            # Determine output directory
            base_out = self.output_dir if self.output_dir else os.path.dirname(filepath)
            
            # Handle independent subfolder
            if self.chk_create_subfolder.isChecked():
                folder_name = os.path.splitext(os.path.basename(filepath))[0]
                final_out_dir = os.path.join(base_out, folder_name)
                if not os.path.exists(final_out_dir):
                    try:
                        os.makedirs(final_out_dir)
                    except OSError as e:
                        logger.error(f"Failed to create directory {final_out_dir}: {e}")
                        self.on_split_error(e, item)
                        continue
            else:
                final_out_dir = base_out
            
            # Track last output dir for auto-open
            self.last_output_dir = final_out_dir
            
            worker = Worker(
                ImageProcessor.split_image, 
                filepath, 
                final_out_dir, 
                output_format=out_fmt,
                rows=rows,
                cols=cols
            )
            # Pass item to callback
            worker.signals.result.connect(lambda res, i=item: self.on_split_finished(res, i))
            worker.signals.error.connect(lambda err, i=item: self.on_split_error(err, i))
            
            self.threadpool.start(worker)

    def on_split_finished(self, result, item):
        try:
            filepath = item.data(Qt.ItemDataRole.UserRole)
            logger.info(f"Split finished for {filepath}")
            item.setText(f"{os.path.basename(filepath)} (完成)")
            item.setForeground(Qt.GlobalColor.green)
            self.check_all_finished()
        except Exception as e:
            logger.error(f"Error in on_split_finished: {e}")

    def on_split_error(self, err, item):
        try:
            filepath = item.data(Qt.ItemDataRole.UserRole)
            item.setText(f"{os.path.basename(filepath)} (失败)")
            item.setForeground(Qt.GlobalColor.red)
            logger.error(f"Split failed: {err}")
            self.check_all_finished()
        except Exception as e:
             logger.error(f"Error in on_split_error: {e}")

    def check_all_finished(self):
        self.active_tasks_count -= 1
        if self.active_tasks_count <= 0:
            logger.info("All tasks finished.")
            if self.chk_auto_open.isChecked() and self.last_output_dir:
                self.open_file_browser(self.last_output_dir)
            self.active_tasks_count = 0

    def open_file_browser(self, path):
        try:
            logger.info(f"Opening folder: {path}")
            if sys.platform == 'win32':
                os.startfile(path)
            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        except Exception as e:
            logger.error(f"Failed to open folder {path}: {e}")

    def process_stitch_task(self, out_fmt):
        count = self.stitch_list.count()
        if count < 2:
            QMessageBox.warning(self, "提示", "请至少添加2张图片进行拼接")
            return

        images = [self.stitch_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(count)]
        
        # Determine output filename
        first_img = images[0]
        base_dir = self.output_dir if self.output_dir else os.path.dirname(first_img)
        filename = f"stitched_{os.path.splitext(os.path.basename(first_img))[0]}"
        output_path = os.path.join(base_dir, filename) # Extension will be added by processor if missing

        mode_map = {
            "等宽缩放": "resize",
            "中心裁剪": "crop",
            "填充背景": "fill"
        }
        mode = mode_map.get(self.stitch_mode_combo.currentText(), "resize")

        self.btn_process.setEnabled(False)
        self.btn_process.setText("拼接中...")

        worker = Worker(
            ImageProcessor.stitch_images,
            images,
            output_path,
            mode=mode,
            output_format=out_fmt
        )
        worker.signals.result.connect(self.on_stitch_finished)
        worker.signals.error.connect(self.on_stitch_error)
        worker.signals.finished.connect(lambda: [self.btn_process.setEnabled(True), self.btn_process.setText("开始处理")])
        
        self.threadpool.start(worker)

    def on_stitch_finished(self, output_path):
        QMessageBox.information(self, "成功", f"拼接完成!\n保存至: {output_path}")
        self.stitch_list.clear()

    def on_stitch_error(self, err):
        QMessageBox.critical(self, "错误", f"拼接失败: {str(err[1])}")
