from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database.connection import DatabaseError
from database.product_repository import get_product_variants
from services.price_service import format_price
from ui.image_loader import load_product_image
from ui.messages import show_error, show_info, show_warning


class ProductPage(QWidget):
    page_title = "Просмотр товара"

    def __init__(self, main_window, product):
        super().__init__()
        self.main_window = main_window
        self.product = product
        self.variants = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(30)

        image_label = QLabel()
        image_label.setFixedSize(340, 260)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setPixmap(load_product_image(product["image_path"], 340, 260))
        layout.addWidget(image_label, 0, Qt.AlignmentFlag.AlignTop)

        info_layout = QVBoxLayout()
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.addRow("Наименование:", self._wrapped_label(product["product_name"]))
        form.addRow("Производство:", self._wrapped_label(product["production"]))
        form.addRow("Категория:", self._wrapped_label(f"{product['category']} / {product['subcategory']}"))
        form.addRow("Цена со скидкой:", self._wrapped_label(format_price(product["final_price"])))
        form.addRow("Состав:", self._wrapped_label(product["composition"]))
        form.addRow("Описание:", self._wrapped_label(product["description"]))

        self.variant_combo = QComboBox()
        form.addRow("Вариант исполнения:", self.variant_combo)
        self.quantity_input = QLineEdit("1")
        self.quantity_input.setValidator(QIntValidator(1, 999, self))
        self.quantity_input.setPlaceholderText("Целое число больше 0")
        self.quantity_input.setMaximumWidth(160)
        form.addRow("Количество:", self.quantity_input)
        info_layout.addLayout(form)

        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить в заказ")
        self.add_button.setObjectName("accentButton")
        self.add_button.clicked.connect(self.add_to_cart)
        buttons_layout.addWidget(self.add_button)
        cart_button = QPushButton("Перейти к заказу")
        cart_button.clicked.connect(self.main_window.open_cart)
        buttons_layout.addWidget(cart_button)
        buttons_layout.addStretch()
        info_layout.addLayout(buttons_layout)
        info_layout.addStretch()
        layout.addLayout(info_layout, 1)

    @staticmethod
    def _wrapped_label(text):
        label = QLabel(text or "—")
        label.setWordWrap(True)
        return label

    def on_show(self):
        self.load_variants()

    def load_variants(self):
        try:
            self.variants = get_product_variants(self.product["product_id"])
        except DatabaseError as error:
            show_error(self, str(error))
            return
        
        self.variant_combo.clear()
        for v in self.variants:
            available = self.get_available_quantity(v)
            if available > 0:
                text = f"{v['variant_name']} (в наличии: {available})"
                self.variant_combo.addItem(text, v)
        has_variants = self.variant_combo.count() > 0
        self.add_button.setEnabled(has_variants)
        if not has_variants:
            self.variant_combo.addItem("Нет в наличии")

    def get_available_quantity(self, variant):
        in_cart = 0
        for item in self.main_window.cart_items:
            if item["product_id"] == self.product["product_id"] and item["variant_id"] == variant["variant_id"]:
                in_cart += item["quantity"]
        return variant["quantity_available"] - in_cart

    def add_to_cart(self):
        variant = self.variant_combo.currentData()
        if variant is None:
            show_warning(self, "Выберите вариант исполнения из списка доступных.")
            return
        quantity_text = self.quantity_input.text().strip()
        if not quantity_text:
            show_warning(self, "Укажите количество.")
            self.quantity_input.setFocus()
            return
        quantity = int(quantity_text)
        available = self.get_available_quantity(variant)
        if quantity <= 0:
            show_error(self, "Количество должно быть больше нуля.")
            return
        if quantity > available:
            show_error(
                self,
                f"Нельзя заказать {quantity} шт. варианта «{variant['variant_name']}»: "
                f"доступно только {available}.",
            )
            return
        self._put_into_cart(variant, quantity)
        self.main_window.update_header()
        self.load_variants()
        show_info(self, f"Добавлено в заказ: {self.product['product_name']} ({variant['variant_name']}), количество {quantity}.")

    def _put_into_cart(self, variant, quantity):
        for item in self.main_window.cart_items:
            if item["product_id"] == self.product["product_id"] and item["variant_id"] == variant["variant_id"]:
                item["quantity"] += quantity
                return
        self.main_window.cart_items.append(
            {
                "product_id": self.product["product_id"],
                "product_name": self.product["product_name"],
                "production": self.product["production"],
                "category": self.product["category"],
                "variant_id": variant["variant_id"],
                "variant_text": variant["variant_name"],
                "quantity": quantity,
                "stock_quantity": variant["quantity_available"],
                "price": variant["variant_price"] if variant["variant_price"] else self.product["final_price"],
            }
        )