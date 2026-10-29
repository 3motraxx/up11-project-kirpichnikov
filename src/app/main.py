import sys

from PySide6.QtCore import QLibraryInfo, QTranslator
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.styles import FONT_FAMILY, STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Мир одежды и аксессуаров")
    
    translator = QTranslator(app)
    if translator.load("qtbase_ru", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(translator)
        
    app.setFont(QFont(FONT_FAMILY, 11))
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()