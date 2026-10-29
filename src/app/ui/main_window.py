from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config import APP_NAME, ICON_PATH, LOGO_PATH
from database.user_repository import get_full_name

ROLE_ADMIN = "Администратор"
ROLE_MANAGER = "Менеджер"


class MainWindow(QMainWindow):
    """Единое окно приложения: шапка с логотипом и ФИО + стек страниц с историей переходов."""

    def __init__(self):
        super().__init__()
        self.current_user = None
        self.cart_items = []
        self.history = []
        self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.resize(1150, 780)
        self.setMinimumSize(950, 650)

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(self._create_header())
        self.pages = QStackedWidget()
        central_layout.addWidget(self.pages)
        self.setCentralWidget(central_widget)

        from ui.login_page import LoginPage

        self.show_root_page(LoginPage(self))

    def _create_header(self):
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(76)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(14, 8, 14, 8)

        logo_label = QLabel()
        logo_pixmap = QPixmap(str(LOGO_PATH))
        if logo_pixmap.isNull():
            logo_label.setText(APP_NAME)
            logo_label.setObjectName("pageTitle")
        else:
            logo_label.setPixmap(
                logo_pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
            )
        layout.addWidget(logo_label)

        self.back_button = QPushButton("← Назад")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.title_label = QLabel()
        self.title_label.setObjectName("pageTitle")
        layout.addWidget(self.title_label, 1, Qt.AlignmentFlag.AlignCenter)

        self.cart_button = QPushButton("Корзина")
        self.cart_button.clicked.connect(self.open_cart)
        layout.addWidget(self.cart_button)

        self.orders_button = QPushButton("Заказы")
        self.orders_button.clicked.connect(self.open_orders)
        layout.addWidget(self.orders_button)

        self.user_label = QLabel()
        self.user_label.setObjectName("userName")
        layout.addWidget(self.user_label)

        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)
        layout.addWidget(self.logout_button)
        return header

    def open_page(self, page):
        current_page = self.pages.currentWidget()
        if current_page is not None:
            self.history.append(current_page)
        self.pages.addWidget(page)
        self._activate(page)

    def show_root_page(self, page):
        while self.pages.count() > 0:
            old_page = self.pages.widget(0)
            self.pages.removeWidget(old_page)
            old_page.deleteLater()
        self.history.clear()
        self.pages.addWidget(page)
        self._activate(page)

    def go_back(self):
        if not self.history:
            return
        current_page = self.pages.currentWidget()
        previous_page = self.history.pop()
        self.pages.removeWidget(current_page)
        current_page.deleteLater()
        self._activate(previous_page)

    def _activate(self, page):
        self.pages.setCurrentWidget(page)
        self.setWindowTitle(f"{APP_NAME} — {page.page_title}")
        self.title_label.setText(page.page_title)
        if hasattr(page, "on_show"):
            page.on_show()
        self.update_header()

    def is_authorized(self):
        return self.current_user is not None

    def is_staff(self):
        return self.is_authorized() and self.current_user["role_name"] in (ROLE_ADMIN, ROLE_MANAGER)

    def is_admin(self):
        return self.is_authorized() and self.current_user["role_name"] == ROLE_ADMIN

    def login(self, user):
        from ui.catalog_page import CatalogPage

        self.current_user = user
        self.cart_items = []
        self.show_root_page(CatalogPage(self))

    def login_as_guest(self):
        from ui.catalog_page import CatalogPage

        self.current_user = None
        self.cart_items = []
        self.show_root_page(CatalogPage(self))

    def logout(self):
        from ui.login_page import LoginPage
        from ui.messages import ask_confirmation

        if self.cart_items:
            confirmed = ask_confirmation(
                self, "В корзине есть неоформленные позиции. При выходе они будут удалены.\nВыйти?"
            )
            if not confirmed:
                return
        self.current_user = None
        self.cart_items = []
        self.show_root_page(LoginPage(self))

    def update_header(self):
        is_login_page = self.pages.currentWidget().__class__.__name__ == "LoginPage"
        self.back_button.setVisible(bool(self.history))
        self.cart_button.setVisible(self.is_authorized())
        self.cart_button.setText(f"Корзина ({len(self.cart_items)})")
        self.orders_button.setVisible(self.is_staff())
        self.logout_button.setVisible(not is_login_page)
        if self.is_authorized():
            self.logout_button.setText("Выйти")
            self.user_label.setText(get_full_name(self.current_user))
        else:
            self.logout_button.setText("Войти")
            self.user_label.setText("" if is_login_page else "Гость")

    def open_cart(self):
        from ui.cart_page import CartPage

        if self.pages.currentWidget().__class__.__name__ == "CartPage":
            return
        self.open_page(CartPage(self))

    def open_orders(self):
        from ui.orders_page import OrdersPage

        if self.pages.currentWidget().__class__.__name__ == "OrdersPage":
            return
        self.open_page(OrdersPage(self))