# --- MENU ---
btn-profile = 👤 My Profile
btn-search = 🎮 Search Games
btn-random = 🎲 Random Game
btn-settings = ⚙️ Settings
btn-back = ⬅️ Back
btn-forward = Forward ➡️
media-btn-cover = 🖼 Cover

# --- ONBOARDING ---
start-welcome-back = 👋 Welcome back, <b>{ $name }</b>!
    You can search for games or check your profile.
start-welcome-new = 👋 <b>Hi! I am Steam Explorer.</b>

    I can help you:
    🔹 Track achievements
    🔹 Search for games
    🔹 Check playtime

    To start, press <b>'👤 My Profile'</b> or just type a game name.

# --- PROFILE ---
profile-info = 👤 <b>Your Profile:</b>
    🆔 Steam ID: <code>{ $steamid }</code>
    📅 Connected: { $date }

    To update library, send /refresh
profile-connect-title = 🔗 <b>Connect Steam</b>
profile-connect-text = Send me a link to your Steam profile or your Steam ID.
    <i>Example: https://steamcommunity.com/id/gaben/</i>
profile-btn-help = ❓ Where to find the link?

# --- ERRORS & STATUS ---
err-profile-not-found = ❌ Profile not found. Check the link.
err-profile-hidden = 🔒 <b>Profile is private!</b>
            I can't see your games. Open them in Steam settings.
status-checking = ⏳ Checking privacy settings...
success-connected = ✅ <b>Success!</b>
    👤 Nickname: { $username }
    🎮 Games in library: { $count }

    Now I know what you play!

# --- SEARCH ---
search-prompt = ✍️ Just type the game name in the chat, and I'll find it.
    <i>Example: Witcher, CS2, Stalker</i>
search-empty = Database is empty so far 😔
search-not-found = ❌ Nothing found for <b>'{ $query }'</b>.
search-found = 🔎 Found games: { $count }. Choose one:

# --- GAME CARD ---
game-gallery = 🖼 <b>Gallery</b> (Use buttons)
game-store-btn = 🛒 Steam Store
game-achievements-btn = 🏆 Achievements
game-trailers-btn = 📹 Trailers
game-update-ru-btn = 🇷🇺 Load RU Data

# GAME CARD BUTTONS
btn-store = 🛒 Steam
btn-achievements = 🏆 Achievements
btn-trailers = 📹 Trailers
btn-to-reqs = 🛠 System Reqs ➡️
btn-to-info = ⬅️ General Info

# Page 1
game-info-header = 🎮 <b>{ $name }</b>
    ⭐️ { $meta }      ⏱️ { $time }

    { $desc }

    📅 { $date }    💰 { $price }
    ➖➖➖➖➖➖➖➖
    🏆 Achievements: { $achievements }   👥 Reviews: { $reviews }
    👨‍💻 Developers: { $devs }

# Page 2
game-reqs-header = 🛠 <b>System Requirements:</b>
    { $reqs }


# --- SETTINGS ---
settings-title = ⚙️ <b>Settings</b>
    Here you can change bot preferences.
settings-lang-btn = 🌐 Language / Язык
settings-select-lang = 🏳️ Choose your language:
settings-lang-changed = ✅ Language changed to <b>English</b>!
    Press /start to update the keyboard.


# ACHIEVEMENTS
ach-rarity-common = 🟢 Common
ach-rarity-rare = 🟡 Rare
ach-rarity-legendary = 🔴 Legendary
ach-locked-desc = 🔒 <i>Hidden achievement. Details will be revealed as you play.</i>
ach-no-desc = No description.
ach-sync-loading = ⏳ Achievements not found. Syncing from Steam...
ach-sync-fail = ❌ No achievements found or Steam error.
ach-empty = Achievement list is empty.
ach-players = players
btn-back-to-game = 🔙 Back to Game

# STEAM SEARCH (Lazy Loading)
search-searching-steam = 🔎 Searching in Steam...
search-downloading = 📥 Downloading game info...
search-steam-error = ❌ Failed to load data from Steam.
search-force-steam = ☁️ search Steam