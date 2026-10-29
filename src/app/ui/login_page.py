from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from database.connection import DatabaseError
from database.user_repository import find_user_by_login
from ui.messages import show_error, show_warning


class LoginPage(QWidget):
    page_title = "Вход в систему"

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        form = QWidget()
        form.setObjectName("toolbar")
        form.setFixedWidth(380)
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(10)

        form_layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин, например client01")
        self.login_input.setMaxLength(50)
        self.login_input.returnPressed.connect(self.try_login)
        form_layout.addWidget(self.login_input)

        login_button = QPushButton("Войти")
        login_button.setObjectName("accentButton")
        login_button.clicked.connect(self.try_login)
        form_layout.addWidget(login_button)

        guest_button = QPushButton("Продолжить как гость")
        guest_button.clicked.connect(self.main_window.login_as_guest)
        form_layout.addWidget(guest_button)

        hint = QLabel("Пароль не требуется. Гостю доступен только просмотр каталога.")
        hint.setObjectName("smallText")
        hint.setWordWrap(True)
        form_layout.addWidget(hint)

        layout = QVBoxLayout(self)
        layout.addWidget(form, 0, Qt.AlignmentFlag.AlignCenter)

    def on_show(self):
        self.login_input.setFocus()

    def try_login(self):
        login = self.login_input.text().strip()
        if not login:
            show_warning(self, "Введите логин, чтобы войти в систему.")
            return
        try:
            user = find_user_by_login(login)
        except DatabaseError as error:
            show_error(self, str(error))
            return
        if user is None:
            show_error(
                self,
                f"Пользователь с логином «{login}» не найден.\n"
                "Проверьте раскладку клавиатуры и правильность логина.",
            )
            return
        self.main_window.login(user)