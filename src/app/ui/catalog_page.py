from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config import LOW_STOCK_LIMIT
from database.connection import DatabaseError
from database.product_repository import get_categories, get_products
from services.price_service import apply_discounts, format_price
from ui.image_loader import load_product_image
from ui.messages import show_error, show_info

ALL_CATEGORIES = "Все категории"
SORT_NONE = "Без сортировки"
SORT_PRICE_ASC = "Цена по возрастанию"
SORT_PRICE_DESC = "Цена по убыванию"


class ProductCard(QFrame):
    clicked = Signal(dict)

    def __init__(self, product):
        super().__init__()
        self.product = product
        is_low_stock = product["total_quantity"] <= LOW_STOCK_LIMIT
        self.setObjectName("productCardLowStock" if is_low_stock else "productCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QGridLayout(self)
        layout.setContentsMargins(12, 10, 24, 10)
        layout.setHorizontalSpacing(24)

        image_label = QLabel()
        image_label.setFixedSize(160, 120)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setPixmap(load_product_image(product["image_path"], 160, 120))
        layout.addWidget(image_label, 0, 0, 4, 1)

        title_label = QLabel(f"{product['production']} | {product['product_name']}")
        title_label.setObjectName("cardTitle")
        title_label.setWordWrap(True)
        layout.addWidget(title_label, 0, 1)

        layout.addWidget(QLabel(f"Категория: {product['category']}"), 1, 1)
        layout.addWidget(QLabel(f"Количество остатков: {product['total_quantity']}"), 2, 1)

        composition_label = QLabel(f"Состав: {product['composition']}")
        composition_label.setObjectName("smallText")
        composition_label.setWordWrap(True)
        layout.addWidget(composition_label, 3, 1)

        price_label = QLabel(self._price_html())
        price_label.setObjectName("cardPrice")
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        price_label.setMinimumWidth(170)
        layout.addWidget(price_label, 0, 2, 4, 1)
        layout.setColumnStretch(1, 1)

    def _price_html(self):
        final_price = format_price(self.product["final_price"])
        if not self.product["has_discount"]:
            return final_price
        old_price = format_price(self.product["price"])
        return f"<span style='font-size:14px; color:#606060;'><s>{old_price}</s></span><br>{final_price}"

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.product)
        super().mousePressEvent(event)


class CatalogPage(QWidget):
    page_title = "Каталог товаров"

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.products = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)

        self.toolbar = QWidget()
        self.toolbar.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(self.toolbar)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по наименованию и описанию")
        self.search_input.textChanged.connect(self.refresh_list)
        toolbar_layout.addWidget(self.search_input, 2)
        self.category_combo = QComboBox()
        self.category_combo.currentIndexChanged.connect(self.refresh_list)
        toolbar_layout.addWidget(self.category_combo, 1)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([SORT_NONE, SORT_PRICE_ASC, SORT_PRICE_DESC])
        self.sort_combo.currentIndexChanged.connect(self.refresh_list)
        toolbar_layout.addWidget(self.sort_combo, 1)
        layout.addWidget(self.toolbar)
        self.toolbar.setVisible(self.main_window.is_authorized())

        self.count_label = QLabel()
        self.count_label.setObjectName("smallText")
        layout.addWidget(self.count_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        list_widget = QWidget()
        self.cards_layout = QVBoxLayout(list_widget)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()
        scroll_area.setWidget(list_widget)
        layout.addWidget(scroll_area)

    def on_show(self):
        self.load_data()

    def load_data(self):
        try:
            self.products = apply_discounts(get_products())
            categories = get_categories()
        except DatabaseError as error:
            show_error(self, str(error))
            return
        selected_category = self.category_combo.currentText()
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem(ALL_CATEGORIES)
        self.category_combo.addItems(categories)
        restored_index = self.category_combo.findText(selected_category)
        self.category_combo.setCurrentIndex(max(restored_index, 0))
        self.category_combo.blockSignals(False)
        self.refresh_list()

    def get_visible_products(self):
        if not self.main_window.is_authorized():
            return list(self.products)
        search_text = self.search_input.text().strip().casefold()
        category = self.category_combo.currentText()
        result = []
        for product in self.products:
            if category != ALL_CATEGORIES and product["category"] != category:
                continue
            searchable_text = f"{product['product_name']} {product['description'] or ''}".casefold()
            if search_text and search_text not in searchable_text:
                continue
            result.append(product)
        sort_mode = self.sort_combo.currentText()
        if sort_mode == SORT_PRICE_ASC:
            result.sort(key=lambda item: item["final_price"])
        elif sort_mode == SORT_PRICE_DESC:
            result.sort(key=lambda item: item["final_price"], reverse=True)
        return result

    def refresh_list(self):
        while self.cards_layout.count() > 1:
            old_card = self.cards_layout.takeAt(0).widget()
            old_card.setParent(None)
            old_card.deleteLater()
        visible_products = self.get_visible_products()
        for product in visible_products:
            card = ProductCard(product)
            card.clicked.connect(self.open_product)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        self.count_label.setText(f"Показано товаров: {len(visible_products)} из {len(self.products)}")

    def open_product(self, product):
        from ui.product_page import ProductPage

        if not self.main_window.is_authorized():
            show_info(
                self,
                "Просмотр карточки и оформление заказа доступны только авторизованным пользователям.\n"
                "Нажмите «Войти» в правом верхнем углу и введите свой логин.",
            )
            return
        self.main_window.open_page(ProductPage(self.main_window, product))