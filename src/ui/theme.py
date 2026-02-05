
from PyQt6.QtGui import QColor, QPalette

class DesignTokens:
    # Fonts
    FONT_FAMILY = "Segoe UI, Microsoft YaHei, Sans-Serif"
    FONT_SIZE_BASE = "16px"
    FONT_SIZE_XL = "20px"
    FONT_SIZE_XXL = "24px"
    FONT_SIZE_DISPLAY = "24px"
    FONT_SIZE_LG = "18px"
    FONT_SIZE_SM = "14px"
    
    # Spacing (Grid System 4px base)
    SPACING_XS = "4px"
    SPACING_SM = "8px"
    SPACING_MD = "16px"
    SPACING_LG = "24px"
    SPACING_XL = "32px"
    
    # Radius
    RADIUS_SM = "4px"
    RADIUS_MD = "8px"
    RADIUS_LG = "12px"
    
    # Animation
    TRANSITION_DURATION = "0.2s"

class LightTheme:
    PRIMARY = "#5B8CFF"
    PRIMARY_HOVER = "#3F74FF"
    PRIMARY_PRESSED = "#2E5BE0"
    ACCENT = "#7C4DFF"
    GRADIENT_START = "#5B8CFF"
    GRADIENT_END = "#7C4DFF"

    BACKGROUND = "#F5F7FB"
    SURFACE = "#FFFFFF"
    SURFACE_SECONDARY = "#F0F3F9"
    SURFACE_TERTIARY = "#E8EDF6"

    TEXT_PRIMARY = "#0F172A" # Slate-900 for higher contrast
    TEXT_SECONDARY = "#475569" # Slate-600
    TEXT_MUTED = "#64748B" # Slate-500, Contrast ~4.9:1 against F5F7FB

    BORDER = "#E2E8F0"
    BORDER_HOVER = "#CBD5E1"
    BORDER_FOCUS = PRIMARY

    SUCCESS = "#22C55E"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"

class DarkTheme:
    PRIMARY = "#7AA2FF"
    PRIMARY_HOVER = "#8CB2FF"
    PRIMARY_PRESSED = "#5B8CFF"
    ACCENT = "#9D7BFF"
    GRADIENT_START = "#5B8CFF"
    GRADIENT_END = "#9D7BFF"

    BACKGROUND = "#0F1220"
    SURFACE = "#161A2B"
    SURFACE_SECONDARY = "#1C2236"
    SURFACE_TERTIARY = "#242B42"

    TEXT_PRIMARY = "#E8ECF6"
    TEXT_SECONDARY = "#A9B2C7"
    TEXT_MUTED = "#7E879C"

    BORDER = "#2C3450"
    BORDER_HOVER = "#3A4466"
    BORDER_FOCUS = PRIMARY

    SUCCESS = "#22C55E"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"

def get_stylesheet(is_dark=False):
    t = DarkTheme if is_dark else LightTheme
    dt = DesignTokens
    
    qss = f"""
    * {{
        font-family: {dt.FONT_FAMILY};
        font-size: {dt.FONT_SIZE_BASE};
        color: {t.TEXT_PRIMARY};
        outline: none;
    }}

    QMainWindow {{
        background-color: {t.BACKGROUND};
    }}

    QWidget {{
        background-color: {t.BACKGROUND};
    }}

    QWidget#TopBar {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.GRADIENT_START}, stop:1 {t.GRADIENT_END});
        border-bottom: 1px solid {t.BORDER};
    }}

    QLabel#AppTitle {{
        font-size: {dt.FONT_SIZE_DISPLAY};
        font-weight: 800;
        color: #FFFFFF;
        background: transparent;
        border: none;
        padding: 0;
        margin: 0;
    }}

    QLabel#AppSubtitle {{
        font-size: {dt.FONT_SIZE_SM};
        color: #FFFFFFEE;
        background: transparent;
        border: none;
        padding: 0;
        margin: 0;
        padding-top: 4px;
    }}

    QLabel#SectionTitle {{
        font-size: {dt.FONT_SIZE_LG};
        font-weight: 600;
        color: {t.TEXT_PRIMARY};
    }}

    QLabel#Caption {{
        font-size: {dt.FONT_SIZE_SM};
        color: {t.TEXT_MUTED};
    }}

    QFrame#SidePanel, QFrame#ContentPanel, QWidget#ContentPanel, QFrame#Card, QWidget#Surface {{
        background-color: {t.SURFACE};
        border: 1px solid {t.BORDER};
        border-radius: {dt.RADIUS_LG};
    }}
    
    /* Remove borders from specific labels to reduce visual noise */
    QLabel {{
        border: none;
        padding: 2px 0;
    }}

    QPushButton {{
        background-color: {t.SURFACE};
        border: 1px solid {t.BORDER};
        border-radius: {dt.RADIUS_MD};
        padding: 8px 16px;
        min-height: 40px;
    }}
    QPushButton:hover {{
        background-color: {t.SURFACE_SECONDARY};
        border-color: {t.BORDER_HOVER};
    }}
    QPushButton:pressed {{
        background-color: {t.SURFACE_TERTIARY};
    }}
    QPushButton:disabled {{
        color: {t.TEXT_MUTED};
        background-color: {t.SURFACE_SECONDARY};
        border-color: {t.BORDER};
    }}
    
    QPushButton#PrimaryButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.GRADIENT_START}, stop:1 {t.GRADIENT_END});
        color: #FFFFFF;
        border: none;
    }}
    QPushButton#PrimaryButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.PRIMARY_HOVER}, stop:1 {t.ACCENT});
    }}
    QPushButton#PrimaryButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.PRIMARY_PRESSED}, stop:1 {t.ACCENT});
    }}

    QPushButton#GhostButton {{
        background-color: transparent;
        border: 1px solid #FFFFFF66;
        color: #FFFFFF;
        padding: 4px 12px;
        min-height: 32px;
    }}
    QPushButton#GhostButton:hover {{
        background-color: #FFFFFF1A;
        border-color: #FFFFFF99;
    }}
    QPushButton#GhostButton:pressed {{
        background-color: #FFFFFF33;
    }}

    QPushButton#ToolButton {{
        padding: 4px;
        min-height: 32px;
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: {dt.RADIUS_MD};
    }}
    QPushButton#ToolButton:hover {{
        background-color: {t.SURFACE_SECONDARY};
        border-color: {t.BORDER_HOVER};
    }}
    QPushButton#ToolButton:pressed {{
        background-color: {t.SURFACE_TERTIARY};
    }}

    QLineEdit, QSpinBox, QComboBox {{
        background-color: {t.SURFACE};
        border: 1px solid {t.BORDER};
        border-radius: {dt.RADIUS_MD};
        padding: 8px;
        min-height: 40px;
        selection-background-color: {t.PRIMARY};
        selection-color: #FFFFFF;
    }}
    QLineEdit:hover, QSpinBox:hover, QComboBox:hover {{
        border-color: {t.BORDER_HOVER};
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 2px solid {t.BORDER_FOCUS};
        padding: 7px;
    }}

    QTabWidget::pane {{
        border: 1px solid {t.BORDER};
        background-color: {t.SURFACE};
        border-radius: {dt.RADIUS_LG};
        top: -1px; 
    }}
    QTabBar::tab {{
        background: transparent;
        border: 1px solid transparent;
        padding: 6px 16px;
        margin-right: 4px;
        border-top-left-radius: {dt.RADIUS_MD};
        border-top-right-radius: {dt.RADIUS_MD};
    }}
    QTabBar::tab:selected {{
        background: {t.SURFACE};
        border-color: {t.BORDER};
        color: {t.PRIMARY};
        font-weight: bold;
    }}
    QTabBar::tab:hover {{
        background: {t.SURFACE_SECONDARY};
    }}

    QListWidget {{
        background-color: {t.SURFACE};
        border: 1px solid {t.BORDER};
        border-radius: {dt.RADIUS_LG};
        padding: 6px;
    }}
    QListWidget::item {{
        border-radius: {dt.RADIUS_MD};
        padding: 6px;
        margin-bottom: 2px;
    }}
    QListWidget::item:selected {{
        background-color: {t.PRIMARY}1A;
        color: {t.TEXT_PRIMARY};
        border: 1px solid {t.PRIMARY}66;
    }}
    QListWidget::item:hover {{
        background-color: {t.SURFACE_SECONDARY};
    }}

    QTableWidget {{
        background-color: {t.SURFACE};
        border: 1px solid {t.BORDER};
        border-radius: {dt.RADIUS_LG};
        gridline-color: {t.BORDER};
    }}
    QTableWidget::item {{
        padding: 8px;
    }}
    QHeaderView::section {{
        background-color: {t.SURFACE_SECONDARY};
        padding: 8px;
        border: none;
        border-right: 1px solid {t.BORDER};
        border-bottom: 1px solid {t.BORDER};
        font-weight: bold;
    }}
    QTableWidget::item:selected {{
        background-color: {t.PRIMARY}33;
        color: {t.TEXT_PRIMARY};
    }}

    QScrollBar:vertical {{
        border: none;
        background: {t.BACKGROUND};
        width: 8px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {t.BORDER};
        min-height: 20px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {t.BORDER_HOVER};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        border: none;
        background: {t.BACKGROUND};
        height: 8px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {t.BORDER};
        min-width: 20px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {t.BORDER_HOVER};
    }}
    
    QProgressBar {{
        border: none;
        background-color: {t.BORDER};
        border-radius: {dt.RADIUS_MD};
        text-align: center;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.GRADIENT_START}, stop:1 {t.GRADIENT_END});
        border-radius: {dt.RADIUS_MD};
    }}

    /* Drop Zone - Dashed border is essential here, kept but softened */
    QLabel#DropZone {{
        border: 2px dashed {t.BORDER};
        border-radius: {dt.RADIUS_LG};
        color: {t.TEXT_SECONDARY};
        font-size: {dt.FONT_SIZE_LG};
        background-color: {t.SURFACE_SECONDARY};
    }}
    QLabel#DropZone:hover {{
        border-color: {t.PRIMARY};
        background-color: {t.PRIMARY}1A;
        color: {t.PRIMARY};
    }}

    /* Remove borders from preview labels for cleaner look, use background only */
    QLabel#PreviewLabel {{
        border: none;
        background-color: {t.SURFACE_SECONDARY};
        border-radius: {dt.RADIUS_LG};
        color: {t.TEXT_SECONDARY};
    }}

    QLabel#PreviewCanvas {{
        border: none;
        background-color: {t.SURFACE_SECONDARY};
        border-radius: {dt.RADIUS_LG};
        color: {t.TEXT_SECONDARY};
    }}

    QCheckBox {{
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1px solid {t.BORDER};
        background-color: {t.SURFACE};
    }}
    QCheckBox::indicator:hover {{
        border-color: {t.BORDER_HOVER};
    }}
    QCheckBox::indicator:checked {{
        background-color: {t.PRIMARY};
        border-color: {t.PRIMARY};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}

    QSplitter::handle {{
        background-color: transparent;
    }}

    QScrollArea {{
        background-color: transparent;
        border: none;
    }}
    """
    return qss
