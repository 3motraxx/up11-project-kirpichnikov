from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from database.connection import DatabaseError
from database.order_repository import delete_order, get_orders
from services.price_service import format_price
from ui.messages import ask_confirmation, show_error, show_info, show_warning
from ui.table_helpers import create_table, fill_table, selected_row


class OrdersPage(QWidget):
    page_title = "Список заказов"

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.orders = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)

        self.table = create_table(["ФИО клиента", "Дата заказа", "Номер заказа", "Сумма"])
        self.table.doubleClicked.connect(self.open_details)
        layout.addWidget(self.table)

        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Добавить заказ")
        add_button.setObjectName("accentButton")
        add_button.clicked.connect(self.add_order)
        buttons_layout.addWidget(add_button)
        details_button = QPushButton("Состав заказа")
        details_button.clicked.connect(self.open_details)
        buttons_layout.addWidget(details_button)
        self.edit_button = QPushButton("Редактировать заказ")
        self.edit_button.clicked.connect(self.edit_order)
        self.edit_button.setVisible(self.main_window.is_admin())
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addStretch()
        delete_button = QPushButton("Удалить заказ")
        delete_button.clicked.connect(self.delete_selected_order)
        buttons_layout.addWidget(delete_button)
        layout.addLayout(buttons_layout)

    def on_show(self):
        self.load_orders()

    def load_orders(self):
        try:
            self.orders = get_orders()
        except DatabaseError as error:
            show_error(self, str(error))
            return
        rows = []
        for order in self.orders:
            rows.append(
                [
                    order["client_name"],
                    order["order_date"].strftime("%d.%m.%Y"),
                    order["order_id"],
                    format_price(order["total_sum"]),
                ]
            )
        fill_table(self.table, rows)

    def get_selected_order(self):
        row = selected_row(self.table)
        if row < 0:
            show_warning(self, "Сначала выберите заказ в таблице.")
            return None
        return self.orders[row]

    def add_order(self):
        from ui.catalog_page import CatalogPage

        self.main_window.open_page(CatalogPage(self.main_window))

    def open_details(self):
        from ui.order_details_page import OrderDetailsPage

        order = self.get_selected_order()
        if order is not None:
            self.main_window.open_page(OrderDetailsPage(self.main_window, order["order_id"], edit_mode=False))

    def edit_order(self):
        from ui.order_details_page import OrderDetailsPage

        if not self.main_window.is_admin():
            show_error(self, "Редактировать заказы может только администратор.")
            return
        order = self.get_selected_order()
        if order is not None:
            self.main_window.open_page(OrderDetailsPage(self.main_window, order["order_id"], edit_mode=True))

    def delete_selected_order(self):
        order = self.get_selected_order()
        if order is None:
            return
        question = (
            f"Удалить заказ №{order['order_id']} от {order['order_date']:%d.%m.%Y} "
            f"({order['client_name']})?\nВместе с заказом будет удалён его состав. Действие необратимо."
        )
        if not ask_confirmation(self, question):
            return
        try:
            delete_order(order["order_id"])
        except DatabaseError as error:
            show_error(self, f"Заказ не удалён.\n{error}")
            return
        show_info(self, f"Заказ №{order['order_id']} удалён.")
        self.load_orders()