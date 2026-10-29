from datetime import date
from decimal import Decimal

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit, QFormLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from database.connection import DatabaseError
from database.order_repository import get_order, get_order_items, update_order
from services.price_service import format_price
from ui.messages import ask_confirmation, show_error, show_info, show_warning
from ui.table_helpers import create_table, fill_table, selected_row


class OrderDetailsPage(QWidget):
    def __init__(self, main_window, order_id, edit_mode):
        super().__init__()
        self.main_window = main_window
        self.order_id = order_id
        self.edit_mode = edit_mode
        self.items = []
        self.removed_item_ids = []
        self.page_title = "Редактирование заказа" if edit_mode else "Состав заказа"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)

        form = QFormLayout()
        self.number_label = QLabel()
        form.addRow("Номер заказа:", self.number_label)
        self.client_label = QLabel()
        form.addRow("Клиент:", self.client_label)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_edit.setEnabled(edit_mode)
        self.date_edit.setMaximumWidth(160)
        form.addRow("Дата заказа:", self.date_edit)
        layout.addLayout(form)

        self.table = create_table(["Товар (наименование | производство)", "Вариант", "Количество", "Цена за ед.", "Сумма"])
        layout.addWidget(self.table)

        self.total_label = QLabel()
        self.total_label.setObjectName("totalLabel")
        layout.addWidget(self.total_label)

        buttons_layout = QHBoxLayout()
        if edit_mode:
            remove_button = QPushButton("Удалить позицию")
            remove_button.clicked.connect(self.remove_item)
            buttons_layout.addWidget(remove_button)
            buttons_layout.addStretch()
            cancel_button = QPushButton("Отмена")
            cancel_button.clicked.connect(self.main_window.go_back)
            buttons_layout.addWidget(cancel_button)
            save_button = QPushButton("Сохранить изменения")
            save_button.setObjectName("accentButton")
            save_button.clicked.connect(self.save_changes)
            buttons_layout.addWidget(save_button)
        else:
            buttons_layout.addStretch()
            back_button = QPushButton("К списку заказов")
            back_button.clicked.connect(self.main_window.go_back)
            buttons_layout.addWidget(back_button)
        layout.addLayout(buttons_layout)

    def on_show(self):
        self.load_order()

    def load_order(self):
        try:
            order = get_order(self.order_id)
            self.items = get_order_items(self.order_id)
        except DatabaseError as error:
            show_error(self, str(error))
            return
        if order is None:
            show_error(self, f"Заказ №{self.order_id} не найден. Возможно, его удалили.")
            return
        self.removed_item_ids.clear()
        self.number_label.setText(str(order["order_id"]))
        self.client_label.setText(order["client_name"])
        order_date = order["order_date"]
        self.date_edit.setDate(QDate(order_date.year, order_date.month, order_date.day))
        self.refresh_table()

    def refresh_table(self):
        rows = []
        total = Decimal(0)
        for item in self.items:
            item_sum = item["price"] * item["quantity"]
            total += item_sum
            rows.append(
                [
                    f"{item['product_name']} | {item['production']}",
                    item["variant_name"],
                    item["quantity"],
                    format_price(item["price"]),
                    format_price(item_sum),
                ]
            )
        fill_table(self.table, rows)
        self.total_label.setText(f"Итоговая сумма заказа: {format_price(total)}")

    def remove_item(self):
        row = selected_row(self.table)
        if row < 0:
            show_warning(self, "Сначала выберите позицию в таблице.")
            return
        if len(self.items) == 1:
            show_warning(
                self,
                "В заказе должна остаться хотя бы одна позиция.\n"
                "Чтобы удалить заказ целиком, используйте кнопку «Удалить заказ» в списке заказов.",
            )
            return
        item = self.items[row]
        if ask_confirmation(self, f"Удалить позицию «{item['product_name']}» ({item['variant_name']})?"):
            self.removed_item_ids.append(item["order_item_id"])
            self.items.pop(row)
            self.refresh_table()

    def save_changes(self):
        new_date = self.date_edit.date().toPython()
        if new_date > date.today():
            show_error(self, "Дата заказа не может быть позже сегодняшней.\nВыберите другую дату.")
            return
        if not ask_confirmation(self, "Сохранить изменения в заказе?"):
            return
        try:
            update_order(self.order_id, new_date, self.removed_item_ids)
        except DatabaseError as error:
            show_error(self, str(error))
            return
        show_info(self, f"Изменения в заказе №{self.order_id} сохранены.")
        self.main_window.go_back()