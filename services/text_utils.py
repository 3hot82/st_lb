import re

# Словарь раскладки
LAYOUT_MAPPING = {
    'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з', '[': 'х', ']': 'ъ',
    'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л', 'l': 'д', ';': 'ж', "'": 'э',
    'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь', ',': 'б', '.': 'ю',
    'й': 'q', 'ц': 'w', 'у': 'e', 'к': 'r', 'е': 't', 'н': 'y', 'г': 'u', 'ш': 'i', 'щ': 'o', 'з': 'p', 'х': '[', 'ъ': ']',
    'ф': 'a', 'ы': 's', 'в': 'd', 'а': 'f', 'п': 'g', 'р': 'h', 'о': 'j', 'л': 'k', 'д': 'l', 'ж': ';', 'э': "'",
    'я': 'z', 'ч': 'x', 'с': 'c', 'м': 'v', 'и': 'b', 'т': 'n', 'ь': 'm', 'б': ',', 'ю': '.'
}

# Сленг
ALIASES = {
    "халфа": "Half-Life", "хл": "Half-Life", "hl": "Half-Life", "hl2": "Half-Life 2",
    "дота": "Dota 2", "кс": "Counter-Strike", "ксго": "Counter-Strike 2",
    "cs": "Counter-Strike 2", "cs2": "Counter-Strike 2",
    "ведьмак": "The Witcher 3", "гта": "Grand Theft Auto V",
    "пабг": "PUBG", "pubg": "PUBG", "тундра": "War Thunder",
    "скайрим": "Skyrim", "смута": "Smuta", "варфрейм": "Warframe"
}

def fix_layout(text: str) -> str:
    return "".join(LAYOUT_MAPPING.get(char, char) for char in text.lower())

def normalize_roman_numerals(text: str) -> str:
    """Меняет 'gta 5' на 'gta v', 'civ 6' на 'civ vi' для улучшения поиска"""
    # Простая замена популярных цифр
    replacements = {
        r'\b1\b': 'I', r'\b2\b': 'II', r'\b3\b': 'III', r'\b4\b': 'IV', 
        r'\b5\b': 'V', r'\b6\b': 'VI', r'\b7\b': 'VII'
    }
    # Мы не меняем сам текст запроса жестко, это вспомогательная функция
    # В данном случае лучше оставить как есть, так как pg_trgm справится сам,
    # но можно использовать для расширения вариантов поиска.
    return text

def clean_query(text: str) -> str:
    """
    Максимальная очистка:
    1. Нижний регистр.
    2. Замена сленга.
    3. Удаление ВСЕХ спецсимволов (оставляем только буквы и цифры и пробелы).
    Это позволит найти 'Half-Life' по запросу 'half life'.
    """
    text = text.lower().strip()
    
    # 1. Сленг
    if text in ALIASES:
        return ALIASES[text].lower()
    
    # 2. Удаляем мусор (™, ®, :)
    text = text.replace("™", "").replace("®", "").replace("©", "")
    
    # 3. Заменяем любые знаки препинания на пробелы (half-life -> half life)
    # Оставляем только буквы, цифры и пробелы
    text = re.sub(r'[^a-zа-я0-9\s]', ' ', text)
    
    # 4. Убираем двойные пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text