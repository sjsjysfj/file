import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.ui.main_window import MainWindow
from src.utils.logger import logger

def main():
    try:
        # Enable High DPI scaling
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        os.environ["QT_SCALE_FACTOR"] = "1"
        
        if hasattr(Qt.HighDpiScaleFactorRoundingPolicy, 'PassThrough'):
            QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Global Font Strategy
        font = app.font()
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
        app.setFont(font)
        
        window = MainWindow()
        window.show()
        
        logger.info("Application started")
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
