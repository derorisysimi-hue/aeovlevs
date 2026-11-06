import random
import time
import os
import sys
import json
import re
import secrets
from datetime import datetime

os.system("")  # ANSI-цвета в Windows

# ───────── Цвета ─────────
R = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
GRAY = "\033[90m"

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")
ANSI_RE = re.compile(r"\033\[[0-9;]*m")


# ───────── Утилиты ─────────
def clear():
    os.system("cls" if os.name == "nt" else "clear")


def vlen(s):
    return len(ANSI_RE.sub("", s))


def box(lines, color=GREEN, width=44):
    print(f"{color}┌{'─' * width}┐{R}")
    for line in lines:
        pad = max(width - vlen(line) - 2, 0)
        print(f"{color}│{R} {line}{' ' * pad} {color}│{R}")
    print(f"{color}└{'─' * width}┘{R}")


def loading(text="Загрузка", seconds=2):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end = time.time() + seconds
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r{CYAN}{frames[i % len(frames)]} {text}...{R}")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write("\r" + " " * (len(text) + 12) + "\r")


def progress(text, seconds=3, color=CYAN):
    steps = 50
    for i in range(steps + 1):
        pct = i / steps
        filled = int(30 * pct)
        sys.stdout.write(
            f"\r  {color}{text} [{'█' * filled}{'░' * (30 - filled)}] {int(pct * 100):>3}%{R}"
        )
        sys.stdout.flush()
        time.sleep(seconds / steps)
    print()


def pause():
    input(f"\n{GRAY}  Нажмите Enter, чтобы продолжить...{R}")


def ask(prompt="Ваш выбор"):
    return input(f"{CYAN}  ➤ {prompt}: {R}").strip()


# ───────── История ─────────
def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# ───────── Генераторы ─────────
def generate_number():
    code = random.randint(900, 999)
    a = random.randint(100, 999)
    b = random.randint(10, 99)
    c = random.randint(10, 99)
    return f"+7 ({code}) {a}-{b}-{c}"


def generate_sms_code():
    return "".join(str(random.randint(0, 9)) for _ in range(5))


# ───────── Интерфейс ─────────
def banner():
    print(f"""{BLUE}{BOLD}
╔══════════════════════════════════════════╗
║                                          ║
║           {MAGENTA}M U L T I - T O O L{BLUE}            ║
║                                          ║
╚══════════════════════════════════════════╝{R}
""")


def header(title, demo=True):
    clear()
    banner()


def show_menu():
    print(f"{YELLOW}{BOLD}  Выберите действие:{R}\n")
    print(f"   {GREEN}[1]{R} Создать номер для Telegram")
    print(f"   {GREEN}[2]{R} История номеров")
    print(f"   {GREEN}[3]{R} Снос аккаунтов по номеру")
    print(f"   {CYAN}[4]{R} Юзернеймы (оценка / генератор)")
    print(f"   {CYAN}[5]{R} Получение галочки")
    print(f"   {CYAN}[6]{R} Верификация Major")
    print(f"   {RED}[0]{R} Выход\n")


def show_sms(number, code):
    print()
    box([
        f"{BOLD}Новое сообщение{R}",
        "─" * 40,
        f"Номер: {number}",
        f"Telegram code: {BOLD}{YELLOW}{code}{R}",
        f"{GRAY}Не передавайте код другим лицам{R}",
    ])


# ───────── [1] Создание номера ─────────
def create_number():
    history = load_history()
    loading("Генерация номера", 2)
    number = generate_number()
    entry = {
        "number": number,
        "code": None,
        "created": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }
    history.append(entry)
    save_history(history)

    print(f"\n{GREEN}  ✔ Номер создан:{R} {BOLD}{YELLOW}{number}{R}")

    while True:
        print(f"\n{YELLOW}{BOLD}  Что дальше?{R}\n")
        print(f"   {GREEN}[1]{R} Посмотреть SMS-код для регистрации")
        print(f"   {RED}[0]{R} Назад в меню\n")
        choice = ask()

        if choice == "1":
            loading("Ожидание SMS", 3)
            code = generate_sms_code()
            entry["code"] = code
            save_history(history)
            show_sms(number, code)
            pause()
            return
        elif choice == "0":
            return
        else:
            print(f"{RED}  Неверный выбор.{R}")


# ───────── [2] История ─────────
def print_history(history):
    print(f"{YELLOW}{BOLD}  История номеров:{R}\n")
    print(f"  {GRAY}{'№':<4}{'Номер':<22}{'Код':<8}Дата{R}")
    print(f"  {GRAY}{'─' * 56}{R}")
    for i, h in enumerate(history, 1):
        code = h["code"] or "—"
        print(f"  {GREEN}{i:<4}{R}{h['number']:<22}{YELLOW}{code:<8}{R}{GRAY}{h['created']}{R}")
    print()


def number_actions(history, idx):
    entry = history[idx]
    while True:
        clear()
        banner()
        box([
            f"{BOLD}Выбран номер{R}",
            f"{entry['number']}",
            f"Последний код: {entry['code'] or '—'}",
            f"Создан: {entry['created']}",
        ], color=CYAN)
        print(f"\n   {GREEN}[1]{R} Прислать новый код")
        print(f"   {RED}[2]{R} Удалить номер")
        print(f"   {GRAY}[0]{R} Назад\n")
        choice = ask()

        if choice == "1":
            loading("Отправка запроса на новый код", 2)
            loading("Ожидание SMS", 2)
            entry["code"] = generate_sms_code()
            save_history(history)
            show_sms(entry["number"], entry["code"])
            pause()
        elif choice == "2":
            confirm = ask("Удалить? (y/n)").lower()
            if confirm == "y":
                history.pop(idx)
                save_history(history)
                print(f"{GREEN}  ✔ Номер удалён.{R}")
                time.sleep(1)
                return
        elif choice == "0":
            return
        else:
            print(f"{RED}  Неверный выбор.{R}")
            time.sleep(1)


def history_menu():
    while True:
        clear()
        banner()
        history = load_history()

        if not history:
            print(f"{GRAY}  История пуста. Сначала создайте номер (пункт 1).{R}")
            pause()
            return

        print_history(history)
        print(f"  {GRAY}Введите номер записи, чтобы выбрать её{R}")
        print(f"  {RED}[c]{R} Очистить всю историю    {GRAY}[0]{R} Назад\n")
        choice = ask()

        if choice == "0":
            return
        elif choice.lower() == "c":
            if ask("Очистить всё? (y/n)").lower() == "y":
                save_history([])
                print(f"{GREEN}  ✔ История очищена.{R}")
                time.sleep(1)
        elif choice.isdigit() and 1 <= int(choice) <= len(history):
            number_actions(history, int(choice) - 1)
        else:
            print(f"{RED}  Неверный выбор.{R}")
            time.sleep(1)


# ───────── [3] Фейковый «снос» ─────────
def fake_takedown():
    header("Снос аккаунтов по номеру")
    print(f"  {GRAY}Введите номер или 'h', чтобы выбрать из истории{R}\n")
    target = ask("Номер")

    if target.lower() == "h":
        history = load_history()
        if not history:
            print(f"{RED}  История пуста.{R}")
            pause()
            return
        print()
        print_history(history)
        pick = ask("Номер записи")
        if pick.isdigit() and 1 <= int(pick) <= len(history):
            target = history[int(pick) - 1]["number"]
        else:
            print(f"{RED}  Неверный выбор.{R}")
            pause()
            return

    if len(re.sub(r"\D", "", target)) < 10:
        print(f"{RED}  Некорректный номер.{R}")
        pause()
        return

    print(f"\n{CYAN}  Цель: {BOLD}{target}{R}\n")
    loading("Поиск аккаунта", 2)
    print(f"{GREEN}  ✔ Аккаунт найден{R}\n")
    time.sleep(0.5)

    reasons = [
        "Спам", "Мошенничество", "Нарушение правил",
        "Фейковый аккаунт", "Рассылка запрещённого контента",
        "Оскорбления", "Подозрительная активность",
    ]

    duration = 10
    steps = 100
    complaints = 0
    bar_len = 30

    print()
    print()
    for step in range(steps + 1):
        pct = step / steps
        filled = int(bar_len * pct)
        bar = "█" * filled + "░" * (bar_len - filled)
        complaints += random.randint(3, 25)
        reason = random.choice(reasons)

        sys.stdout.write("\033[2F")
        sys.stdout.write(f"\033[2K  {RED}[{bar}]{R} {int(pct * 100):>3}%\n")
        sys.stdout.write(
            f"\033[2K  {YELLOW}Жалоб отправлено: {BOLD}{complaints}{R}"
            f"{GRAY}  • {reason}{R}\n"
        )
        sys.stdout.flush()
        time.sleep(duration / steps)

    print()
    box([
        f"{BOLD}{GREEN}АККАУНТ УСПЕШНО СНЕСЁН{R}",
        "─" * 40,
        f"Номер: {target}",
        f"Жалоб отправлено: {complaints}",
        f"Статус: {RED}заблокирован{R}",
    ])
    pause()


# ───────── [4] Юзернеймы (реальная логика) ─────────
VOWELS = "aeiouy"
CONSONANTS = "bcdfghjklmnprstvwz"
WORDS = [
    "wolf", "fox", "ghost", "storm", "byte", "hawk", "ninja", "king", "tiger",
    "neon", "dark", "frost", "pixel", "shadow", "turbo", "cyber", "lucky",
    "wild", "star", "moon", "fire", "zen", "nova", "core", "flow", "wave",
]


def validate_username(name):
    errors = []
    if not 5 <= len(name) <= 32:
        errors.append("Длина должна быть от 5 до 32 символов")
    if not re.fullmatch(r"[a-z0-9_]*", name):
        errors.append("Допустимы только a–z, 0–9 и _")
    if name and not name[0].isalpha():
        errors.append("Должен начинаться с буквы")
    if name.endswith("_"):
        errors.append("Не может заканчиваться на _")
    if "__" in name:
        errors.append("Нельзя два подчёркивания подряд")
    return errors


def score_username(name):
    """Возвращает (оценка 0–100, список заметок)."""
    score = 0
    notes = []
    n = len(name)

    # Длина
    length_pts = {5: 30, 6: 25, 7: 20, 8: 15, 9: 10, 10: 10}.get(n, 5 if n <= 14 else 0)
    score += length_pts
    notes.append((length_pts >= 20, f"Длина {n} симв. ({'коротко' if length_pts >= 20 else 'длинновато'})"))

    # Цифры
    digits = sum(c.isdigit() for c in name)
    if digits == 0:
        score += 15
        notes.append((True, "Без цифр"))
    else:
        score -= min(digits * 5, 15)
        notes.append((False, f"Цифр: {digits}"))

    # Подчёркивания
    us = name.count("_")
    if us == 0:
        score += 10
        notes.append((True, "Без подчёркиваний"))
    else:
        score -= us * 5
        notes.append((False, f"Подчёркиваний: {us}"))

    # Читаемость (чередование гласных и согласных)
    letters = [c for c in name if c.isalpha()]
    if len(letters) > 1:
        pairs = sum((a in VOWELS) != (b in VOWELS) for a, b in zip(letters, letters[1:]))
        ratio = pairs / (len(letters) - 1)
        score += int(25 * ratio)
        notes.append((ratio >= 0.6, f"Читаемость: {int(ratio * 100)}%"))

    # Слово из словаря
    found = [w for w in WORDS if w in name]
    if found:
        score += 10
        notes.append((True, f"Содержит слово «{found[0]}»"))

    # Три одинаковых символа подряд
    if re.search(r"(.)\1\1", name):
        score -= 10
        notes.append((False, "Три одинаковых символа подряд"))

    # Красивые паттерны: палиндром, abab, aabb
    if name == name[::-1] or re.fullmatch(r"(.{1,2})\1+", name) or re.fullmatch(r"(.)\1(.)\2", name):
        score += 5
        notes.append((True, "Красивый паттерн"))

    return max(0, min(score, 100)), notes


def rating_label(score):
    if score >= 80:
        return f"{GREEN}{BOLD}ТОП{R}"
    if score >= 60:
        return f"{GREEN}Отличный{R}"
    if score >= 40:
        return f"{YELLOW}Нормальный{R}"
    return f"{RED}Слабый{R}"


def score_bar(score):
    filled = score * 20 // 100
    color = GREEN if score >= 60 else YELLOW if score >= 40 else RED
    return f"{color}{'█' * filled}{'░' * (20 - filled)}{R} {score}/100"


def evaluate_username():
    header("Оценка юзернейма", demo=False)
    name = ask("Юзернейм").lower().lstrip("@")
    if not name:
        return

    errors = validate_username(name)
    print()
    if errors:
        box([f"{RED}{BOLD}Юзернейм недопустим{R}"] + [f"{RED}✖{R} {e}" for e in errors], color=RED)
        pause()
        return

    loading("Анализ", 1.5)
    score, notes = score_username(name)
    lines = [
        f"{BOLD}@{name}{R}",
        "─" * 40,
        score_bar(score),
        f"Рейтинг: {rating_label(score)}",
        "─" * 40,
    ]
    for ok, text in notes:
        mark = f"{GREEN}✔" if ok else f"{RED}✖"
        lines.append(f"{mark}{R} {text}")
    lines += ["─" * 40, f"{GRAY}Проверить занятость: t.me/{name}{R}"]
    box(lines, color=CYAN)
    pause()


def make_candidate(n):
    if random.random() < 0.33:
        return random.choice(WORDS) + random.choice(WORDS)
    # Произносимый ник: согласная-гласная-...
    start_vowel = random.random() < 0.15
    out = []
    for i in range(n):
        use_vowel = (i % 2 == 0) == start_vowel
        out.append(secrets.choice(VOWELS if use_vowel else CONSONANTS))
    return "".join(out)


def generate_usernames():
    header("Генератор крутых юзернеймов", demo=False)
    n = ask("Желаемая длина (5–10, по умолчанию 6)")
    n = int(n) if n.isdigit() else 6
    n = max(5, min(n, 10))

    loading("Подбор вариантов", 2)
    pool = set()
    for _ in range(600):
        c = make_candidate(n)
        if not validate_username(c):
            pool.add(c)

    ranked = sorted(((score_username(c)[0], c) for c in pool), reverse=True)
    top = ranked[:8]

    print(f"\n{YELLOW}{BOLD}  Лучшие варианты:{R}\n")
    for sc, c in top:
        print(f"   {GREEN}▸{R} {BOLD}{CYAN}@{c:<14}{R} {score_bar(sc)}")
    print(f"\n  {GRAY}Занятость проверяй вручную: t.me/ник{R}")
    pause()


def username_menu():
    while True:
        header("Юзернеймы", demo=False)
        print(f"   {GREEN}[1]{R} Оценить текущий юзернейм")
        print(f"   {GREEN}[2]{R} Создать новый крутой юзернейм")
        print(f"   {GRAY}[0]{R} Назад\n")
        c = ask()
        if c == "1":
            evaluate_username()
        elif c == "2":
            generate_usernames()
        elif c == "0":
            return
        else:
            print(f"{RED}  Неверный выбор.{R}")
            time.sleep(1)


# ───────── [5] Галочка (фейк) ─────────
def fake_checkmark():
    header("Получение галочки по юзернейму")
    user = ask("Ваш @username")
    if not user:
        return
    user = user if user.startswith("@") else "@" + user

    print()
    progress("Поиск профиля      ", 2)
    progress("Отправка заявки    ", 2)
    progress("Модерация          ", 3, YELLOW)
    progress("Выдача галочки     ", 2, GREEN)
    print()
    box([
        f"{BOLD}{GREEN}ГАЛОЧКА ВЫДАНА ✔{R}",
        "─" * 40,
        f"Аккаунт: {user}",
        f"Статус: {CYAN}Verified{R}",
    ])
    pause()


# ───────── [6] Верификация Major (фейк) ─────────
def fake_major():
    header("Верификация Major")
    user = ask("Ваш @username")
    if not user:
        return
    user = user if user.startswith("@") else "@" + user

    print()
    loading("Подключение к Major", 2)
    progress("Проверка аккаунта  ", 2)
    progress("Анализ активности  ", 3, YELLOW)
    progress("Подтверждение      ", 2, GREEN)
    print()
    box([
        f"{BOLD}{GREEN}ВЕРИФИКАЦИЯ MAJOR ПРОЙДЕНА{R}",
        "─" * 40,
        f"Аккаунт: {user}",
        f"Статус: {GREEN}подтверждён{R}",
    ])
    pause()


# ───────── Главный цикл ─────────
def main():
    actions = {
        "1": create_number,
        "2": history_menu,
        "3": fake_takedown,
        "4": username_menu,
        "5": fake_checkmark,
        "6": fake_major,
    }
    while True:
        clear()
        banner()
        show_menu()
        choice = ask()
        if choice in actions:
            actions[choice]()
        elif choice == "0":
            print(f"\n{GRAY}  Выход... До встречи!{R}")
            break
        else:
            print(f"{RED}  Неверный выбор!{R}")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{GRAY}  Прервано пользователем.{R}")