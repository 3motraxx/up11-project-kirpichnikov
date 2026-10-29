MAIN_BACKGROUND = "#FFFFFF"
SECONDARY_BACKGROUND = "#D2F6E7"
ACCENT_COLOR = "#70B2AF"
LOW_STOCK_COLOR = "#FF8080"
FONT_FAMILY = "Calibri"

STYLESHEET = f"""
QWidget {{
    font-family: "{FONT_FAMILY}";
    font-size: 14px;
    color: #000000;
}}
QMainWindow, QStackedWidget, QScrollArea, QScrollArea > QWidget > QWidget {{
    background-color: {MAIN_BACKGROUND};
}}
#header {{
    background-color: {SECONDARY_BACKGROUND};
}}
#pageTitle {{
    font-size: 20px;
    font-weight: bold;
}}
#userName {{
    font-size: 14px;
    font-weight: bold;
}}
#toolbar {{
    background-color: {SECONDARY_BACKGROUND};
    border-radius: 6px;
}}
QPushButton {{
    background-color: {MAIN_BACKGROUND};
    border: 1px solid {ACCENT_COLOR};
    border-radius: 5px;
    padding: 6px 14px;
}}
QPushButton:hover {{
    background-color: {SECONDARY_BACKGROUND};
}}
QPushButton#accentButton {{
    background-color: {ACCENT_COLOR};
    color: #FFFFFF;
    font-weight: bold;
}}
QPushButton:disabled {{
    color: #999999;
    border-color: #CCCCCC;
}}
QLineEdit, QComboBox, QDateEdit {{
    background-color: {MAIN_BACKGROUND};
    border: 1px solid #A0A0A0;
    border-radius: 4px;
    padding: 4px 6px;
    min-height: 22px;
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
    border: 1px solid {ACCENT_COLOR};
}}
QTableWidget {{
    background-color: {MAIN_BACKGROUND};
    gridline-color: #C8C8C8;
    selection-background-color: {ACCENT_COLOR};
    selection-color: #FFFFFF;
}}
QHeaderView::section {{
    background-color: {SECONDARY_BACKGROUND};
    padding: 5px;
    border: none;
    border-right: 1px solid #C8C8C8;
    font-weight: bold;
}}
#productCard {{
    background-color: {MAIN_BACKGROUND};
    border: 1px solid #808080;
}}
#productCardLowStock {{
    background-color: {LOW_STOCK_COLOR};
    border: 1px solid #808080;
}}
#productCard QLabel, #productCardLowStock QLabel {{
    background-color: transparent;
}}
#cardTitle {{
    font-size: 17px;
}}
#cardPrice {{
    font-size: 22px;
}}
#smallText {{
    font-size: 12px;
}}
#totalLabel {{
    font-size: 17px;
    font-weight: bold;
}}
"""