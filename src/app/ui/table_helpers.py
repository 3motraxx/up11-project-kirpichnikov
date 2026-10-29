from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem


def create_table(columns):
    table = QTableWidget()
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels(columns)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    return table


def fill_table(table, rows):
    table.setRowCount(len(rows))
    for row_idx, row in enumerate(rows):
        for col_idx, value in enumerate(row):
            item = QTableWidgetItem(str(value))
            table.setItem(row_idx, col_idx, item)


def selected_row(table):
    selected = table.selectedIndexes()
    if not selected:
        return -1
    return selected[0].row()