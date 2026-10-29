from PySide6.QtWidgets import QMessageBox


def show_error(parent, text):
    QMessageBox.critical(parent, "Ошибка", text)


def show_warning(parent, text):
    QMessageBox.warning(parent, "Предупреждение", text)


def show_info(parent, text):
    QMessageBox.information(parent, "Информация", text)


def ask_confirmation(parent, text):
    answer = QMessageBox.question(
        parent,
        "Подтверждение действия",
        text,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return answer == QMessageBox.StandardButton.Yes