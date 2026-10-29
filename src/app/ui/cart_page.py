from decimal import Decimal

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QInputDialog, QLabel, QPushButton, QVBoxLayout, QWidget

from database.connection import DatabaseError
from database.order_repository import create_order
from database.user_repository import get_all_users, get_full_name
from services.price_service import format_price
from ui.messages import ask_confirmation, show_error, show_info, show_warning
from ui.table_helpers import create_table, fill_table, selected_row


class CartPage(QWidget):
    page_title = "Оформление заказа"

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)

        client_layout = QHBoxLayout()
        self.client_label = QLabel("Клиент:")
        client_layout.addWidget(self.client_label)
        self.client_combo = QComboBox()
        self.client_combo.setMinimumWidth(320)
        client_layout.addWidget(self.client_combo)
        client_layout.addStretch()
        layout.addLayout(client_layout)

        self.table = create_table(["Наименование", "Вариант", "Количество", "Цена за ед.", "Сумма"])
        layout.addWidget(self.table)

        self.total_label = QLabel()
        self.total_label.setObjectName("totalLabel")
        layout.addWidget(self.total_label)

        buttons_layout = QHBoxLayout()
        change_button = QPushButton("Изменить количество")
        change_button.clicked.connect(self.change_quantity)
        buttons_layout.addWidget(change_button)
        remove_button = QPushButton("Удалить позицию")
        remove_button.clicked.connect(self.remove_item)
        buttons_layout.addWidget(remove_button)
        add_more_button = QPushButton("Добавить товар")
        add_more_button.clicked.connect(self.go_to_catalog)
        buttons_layout.addWidget(add_more_button)
        buttons_layout.addStretch()
        cancel_button = QPushButton("Отказаться от заказа")
        cancel_button.clicked.connect(self.cancel_order)
        buttons_layout.addWidget(cancel_button)
        confirm_button = QPushButton("Подтвердить заказ")
        confirm_button.setObjectName("accentButton")
        confirm_button.clicked.connect(self.confirm_order)
        buttons_layout.addWidget(confirm_button)
        layout.addLayout(buttons_layout)

        self.load_clients()

    def load_clients(self):
        is_staff = self.main_window.is_staff()
        self.client_label.setVisible(is_staff)
        self.client_combo.setVisible(is_staff)
        if not is_staff:
            return
        try:
            users = get_all_users()
        except DatabaseError as error:
            show_error(self, str(error))
            return
        for user in users:
            self.client_combo.addItem(f"{get_full_name(user)} ({user['login']})", user["user_id"])
        own_index = self.client_combo.findData(self.main_window.current_user["user_id"])
        self.client_combo.setCurrentIndex(max(own_index, 0))

    def on_show(self):
        self.refresh_table()

    def refresh_table(self):
        rows = []
        total = Decimal(0)
        for item in self.main_window.cart_items:
            item_sum = item["price"] * item["quantity"]
            total += item_sum
            rows.append(
                [
                    f"{item['product_name']} | {item['production']}",
                    item["variant_text"],
                    item["quantity"],
                    format_price(item["price"]),
                    format_price(item_sum),
                ]
            )
        fill_table(self.table, rows)
        self.total_label.setText(f"Итого: {format_price(total)}")
        self.main_window.update_header()

    def get_selected_item(self):
        row = selected_row(self.table)
        if row < 0:
            show_warning(self, "Сначала выберите позицию в таблице.")
            return None
        return self.main_window.cart_items[row]

    def change_quantity(self):
        item = self.get_selected_item()
        if item is None:
            return
        new_quantity, accepted = QInputDialog.getInt(
            self,
            "Изменение количества",
            f"Количество (от 1 до {item['stock_quantity']}):",
            item["quantity"],
            1,
            item["stock_quantity"],
        )
        if accepted:
            item["quantity"] = new_quantity
            self.refresh_table()

    def remove_item(self):
        item = self.get_selected_item()
        if item is None:
            return
        question = f"Удалить из заказа «{item['product_name']}» ({item['variant_text']})?"
        if ask_confirmation(self, question):
            self.main_window.cart_items.remove(item)
            self.refresh_table()

    def go_to_catalog(self):
        from ui.catalog_page import CatalogPage

        self.main_window.open_page(CatalogPage(self.main_window))

    def cancel_order(self):
        if not self.main_window.cart_items:
            show_info(self, "Заказ пуст — отменять нечего.")
            return
        if ask_confirmation(self, "Отказаться от оформления заказа? Все позиции будут удалены из корзины."):
            self.main_window.cart_items.clear()
            self.refresh_table()
            show_info(self, "Оформление заказа отменено.")

    def confirm_order(self):
        if not self.main_window.cart_items:
            show_warning(self, "В заказе нет ни одной позиции.\nДобавьте товары из каталога.")
            return
        client_id = self.main_window.current_user["user_id"]
        if self.main_window.is_staff():
            client_id = self.client_combo.currentData()
        if not ask_confirmation(self, "Подтвердить и оформить заказ?"):
            return
        try:
            order_id = create_order(client_id, self.main_window.cart_items)
        except DatabaseError as error:
            show_error(self, str(error))
            return
        self.main_window.cart_items.clear()
        show_info(self, f"Заказ №{order_id} успешно оформлен.")
        self.return_after_order()

    def return_after_order(self):
        from ui.catalog_page import CatalogPage
        from ui.orders_page import OrdersPage

        self.main_window.show_root_page(CatalogPage(self.main_window))
        if self.main_window.is_staff():
            self.main_window.open_page(OrdersPage(self.main_window))