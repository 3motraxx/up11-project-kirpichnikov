from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap

from config import IMAGES_DIR, PLACEHOLDER_PATH

_cache = {}


def _draw_empty_picture(width, height):
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#EEEEEE"))
    painter = QPainter(pixmap)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Нет фото")
    painter.end()
    return pixmap


def load_product_image(image_path, width, height):
    cache_key = (image_path, width, height)
    if cache_key in _cache:
        return _cache[cache_key]
    pixmap = QPixmap()
    if image_path:
        pixmap.load(str(IMAGES_DIR / image_path))
    if pixmap.isNull():
        pixmap.load(str(PLACEHOLDER_PATH))
    if pixmap.isNull():
        pixmap = _draw_empty_picture(width, height)
    scaled = pixmap.scaled(
        width,
        height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    _cache[cache_key] = scaled
    return scaled