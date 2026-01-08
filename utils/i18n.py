from pathlib import Path
from fluent.runtime import FluentLocalization, FluentResourceLoader

# Указываем путь к папке locales
locales_path = Path(__file__).parent.parent / "locales"

# Загрузчик ресурсов
loader = FluentResourceLoader(str(locales_path) + "/{locale}")

def get_l10n(locale: str = "ru"):
    """Возвращает объект локализации для конкретного языка"""
    # Если языка нет, fluent сам откатится (но лучше иметь fallback)
    return FluentLocalization([locale, "ru"], ["strings.ftl"], loader)