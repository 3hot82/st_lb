# --- КНОПКИ МЕНЮ ---
btn-profile = 👤 Мой профиль
btn-search = 🎮 Поиск игр
btn-random = 🎲 Случайная игра
btn-settings = ⚙️ Настройки
btn-back = ⬅️ Назад
btn-forward = Вперед ➡️
media-btn-cover = 🖼 Обложка
# --- ONBOARDING (ПРИВЕТСТВИЕ) ---
start-welcome-back = 👋 С возвращением, <b>{ $name }</b>!
    Ты можешь искать игры или посмотреть свой профиль.
start-welcome-new = 👋 <b>Привет! Я Steam Explorer.</b>

    Я помогу тебе:
    🔹 Следить за ачивками
    🔹 Искать игры
    🔹 Узнать время прохождения

    Чтобы начать, нажми кнопку <b>'👤 Мой профиль'</b> или просто напиши название игры.

# --- ПРОФИЛЬ ---
profile-info = 👤 <b>Твой профиль:</b>
    🆔 Steam ID: <code>{ $steamid }</code>
    📅 Дата подключения: { $date }

    Чтобы обновить библиотеку игр, отправь /refresh
profile-connect-title = 🔗 <b>Привязка Steam</b>
profile-connect-text = Пришли мне ссылку на твой профиль Steam или твой Steam ID.
    <i>Пример: https://steamcommunity.com/id/gaben/</i>
profile-btn-help = ❓ Где взять ссылку?

# --- ОШИБКИ И СТАТУСЫ ---
err-profile-not-found = ❌ Не удалось найти такой профиль. Проверь ссылку.
err-profile-hidden = 🔒 <b>Профиль скрыт!</b>
    Я не вижу твои игры. Открой их в настройках Steam.
status-checking = ⏳ Проверяю настройки приватности...
success-connected = ✅ <b>Успешно!</b>
    👤 Ник: { $username }
    🎮 Игр в библиотеке: { $count }

    Теперь я знаю, во что ты играешь!

# --- ПОИСК ---
search-prompt = ✍️ Просто напиши название игры в чат, и я найду её.
    <i>Например: Ведьмак, CS2, Stalker</i>
search-empty = В базе пока пусто 😔
search-not-found = ❌ По запросу <b>'{ $query }'</b> ничего не найдено.
search-found = 🔎 Найдено игр: { $count }. Выбери нужную:

# --- КАРТОЧКА ИГРЫ ---
game-gallery = 🖼 <b>Галерея</b> (Листай кнопками)
game-store-btn = 🛒 Steam Store
game-achievements-btn = 🏆 Ачивки
game-trailers-btn = 📹 Трейлеры
game-update-ru-btn = 🇷🇺 Загрузить RU
# КНОПКИ КАРТОЧКИ ИГРЫ
btn-store = 🛒 Steam
btn-achievements = 🏆 Ачивки
btn-trailers = 📹 Трейлеры
btn-to-reqs = 🛠 Системные требования ➡️
btn-to-info = ⬅️ Общая информация
# Страница 1
game-info-header = 🎮 <b>{ $name }</b>
    ⭐️ { $meta }      ⏱️ { $time }

    { $desc }

    📅 { $date }    💰 { $price }
    ➖➖➖➖➖➖➖➖
    🏆 Ачивок: { $achievements }   👥 Отзывов: { $reviews }
    👨‍💻 Разработчики: { $devs }

# Страница 2
game-reqs-header = 🛠 <b>Системные требования:</b>
    { $reqs }

# --- НАСТРОЙКИ ---
settings-title = ⚙️ <b>Настройки</b>
    Здесь ты можешь изменить параметры бота.
settings-lang-btn = 🌐 Язык / Language
settings-select-lang = 🏳️ Выберите язык:
settings-lang-changed = ✅ Язык изменен на <b>Русский</b>!
    Нажми /start, чтобы обновить клавиатуру.

# АЧИВКИ
ach-rarity-common = 🟢 Обычная
ach-rarity-rare = 🟡 Редкая
ach-rarity-legendary = 🔴 Легендарная
ach-locked-desc = 🔒 <i>Это скрытое достижение. Подробности раскрываются по ходу игры.</i>
ach-no-desc = Описание отсутствует.
ach-sync-loading = ⏳ Ачивки не найдены. Загружаю из Steam...
ach-sync-fail = ❌ У этой игры нет ачивок или ошибка Steam.
ach-empty = Список ачивок пуст.
ach-players = игроков
btn-back-to-game = 🔙 К игре

search-searching-steam = 🔎 Ищу в Steam...
search-downloading = 📥 Загружаю информацию об игре...
search-steam-error = ❌ Ошибка загрузки данных из Steam.
search-force-steam = ☁️ Найти в Steam