import tkinter as tk
from tkinter import ttk, StringVar, messagebox
from datetime import datetime
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import calendar
import pandas as pd

# Путь к файлу данных
DATA_FILE = "emotions.json"

# Словарь эмоций с описаниями и эмодзи
EMOTIONS = {
    "Счастье": {"desc": "Чувство радости и удовлетворения", "emoji": "😊"},
    "Грусть": {"desc": "Ощущение печали или утраты", "emoji": "😢"},
    "Страх": {"desc": "Чувство тревоги или беспокойства", "emoji": "😱"},
    "Злость": {"desc": "Эмоция, связанная с раздражением или агрессией", "emoji": "😡"},
    "Удивление": {"desc": "Реакция на что-то неожиданное или необычное", "emoji": "😲"},
    "Отвращение": {"desc": "Чувство неприязни или неприятия", "emoji": "🤢"},
    "Спокойствие": {"desc": "Состояние умиротворения и внутреннего покоя", "emoji": "🧘"},
    "Волнение": {"desc": "Смесь радости и тревоги, часто перед важными событиями", "emoji": "😅"},
    "Уверенность": {"desc": "Чувство веры в свои силы и способности", "emoji": "💪"},
    "Непонимание": {"desc": "Эмоция, возникающая при столкновении с чем-то сложным или запутанным", "emoji": "🤔"}
}

# Цвета и стили
FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 12
FONT_SIZE_LARGE = 14
FONT_SIZE_HEADER = 16
COLOR_BG = "#F9FAFB"
COLOR_PRIMARY = "#3B82F6"
COLOR_BUTTON_BG = "#BFDBFE"
COLOR_BUTTON_HOVER = "#93C5FD"

# Загрузка данных из файла
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Сохранение данных в файл
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Глобальная переменная для хранения выбранной даты
selected_date = None

# Сохранение новой эмоции + заметки
def save_emotion():
    global selected_date, note_text
    emotion = combo_emotion.get()
    note = note_text.get("1.0", tk.END).strip()
    if not selected_date or not emotion:
        messagebox.showwarning("Ошибка", "Пожалуйста, выберите дату и эмоцию.")
        return
    data = load_data()
    data[selected_date] = {"emotion": emotion, "note": note}
    save_data(data)
    update_calendar_view()
    clear_form()
    print(f"Сохранено: {selected_date} - {emotion}")

# Очистка формы
def clear_form():
    global selected_date, note_text
    selected_date = None
    combo_emotion.set("")
    label_selected_date.config(text="Дата не выбрана")
    description_var.set("")
    note_text.delete("1.0", tk.END)

# Простой класс для отображения подсказок
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x = y = 0
        x = self.widget.winfo_pointerx() + 10
        y = self.widget.winfo_pointery() + 10
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, bg="yellow", font=(FONT_FAMILY, 10), padx=5, pady=2).pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# === Функция создания календаря в главном окне ===
def create_calendar_grid(parent_frame):
    month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                   "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    current_month = datetime.now().month
    current_year = datetime.now().year
    calendar_frame = tk.Frame(parent_frame, bg=COLOR_BG)
    calendar_frame.pack(pady=10)
    control_frame = tk.Frame(calendar_frame, bg=COLOR_BG)
    control_frame.grid(row=0, column=0, columnspan=7, sticky="ew")
    month_var = tk.IntVar(value=current_month)
    year_var = tk.IntVar(value=current_year)
    title_label = tk.Label(control_frame, text="", font=(FONT_FAMILY, FONT_SIZE_HEADER, "bold"), fg="black", bg=COLOR_BG)
    title_label.pack(side="top")

    def update_calendar_display():
        for widget in calendar_frame.winfo_children():
            if widget != control_frame:
                widget.destroy()
        month = month_var.get()
        year = year_var.get()
        title_label.config(text=f"{month_names[month - 1]} {year}")
        days_short = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(days_short):
            tk.Label(calendar_frame, text=day, font=(FONT_FAMILY, FONT_SIZE_NORMAL), fg="#555", bg=COLOR_BG).grid(
                row=1, column=i, pady=5)

        first_day, num_days = calendar.monthrange(year, month)
        first_day = (first_day + 1) % 7  # Monday is 0
        row, col = 2, first_day
        data = load_data()
        for day_num in range(1, num_days + 1):
            date_str = f"{year}-{str(month).zfill(2)}-{str(day_num).zfill(2)}"
            emoji = "⚪️"
            emotion = ""
            note = ""
            if date_str in data:
                emotion = data[date_str]["emotion"]
                emoji = EMOTIONS.get(emotion, {}).get("emoji", "❓")
                note = data[date_str].get("note", "")
            lbl = tk.Label(calendar_frame, text=emoji, font=("Arial", 24), width=4, height=2,
                           relief="groove", bg="white", cursor="hand2")
            lbl.grid(row=row, column=col, padx=4, pady=4)
            Tooltip(lbl, f"Дата: {date_str}\nЭмоция: {emotion if emotion else 'Нет данных'}\nЗаметка: {note if note else 'Нет заметки'}")

            def on_click(event, d=date_str):
                global selected_date
                selected_date = d
                label_selected_date.config(text=f"Выбрана дата: {selected_date}")
                data = load_data()
                if d in data:
                    combo_emotion.set(data[d]["emotion"])
                    description_var.set(EMOTIONS.get(data[d]["emotion"], {}).get("desc", ""))
                    note_text.delete("1.0", tk.END)
                    note_text.insert(tk.END, data[d].get("note", ""))
                else:
                    combo_emotion.set("")
                    description_var.set("")
                    note_text.delete("1.0", tk.END)

            def on_shift_click(event, d=date_str):
                select_emoji_window(d)

            def handle_click(event, d=date_str):
                if event.state & 0x0001:  # Shift нажат
                    on_shift_click(event, d)
                else:
                    on_click(event, d)

            def on_double_click(event, d=date_str):
                if d in data:
                    if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить эмоцию за {d}?"):
                        del data[d]
                        save_data(data)
                        update_calendar_view()
                        print(f"Запись за {d} удалена")

            lbl.bind("<Button-1>", handle_click)
            lbl.bind("<Double-1>", on_double_click)
            col += 1
            if col > 6:
                col = 0
                row += 1

    def change_month(delta):
        new_month = month_var.get() + delta
        new_year = year_var.get()
        if new_month < 1:
            new_month = 12
            new_year -= 1
        elif new_month > 12:
            new_month = 1
            new_year += 1
        month_var.set(new_month)
        year_var.set(new_year)
        update_calendar_display()

    btn_prev = tk.Button(control_frame, text="⬅", command=lambda: change_month(-1),
                         font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                         bg=COLOR_BUTTON_BG, activebackground=COLOR_BUTTON_HOVER, bd=0, padx=10, pady=5)
    btn_next = tk.Button(control_frame, text="➡", command=lambda: change_month(1),
                         font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                         bg=COLOR_BUTTON_BG, activebackground=COLOR_BUTTON_HOVER, bd=0, padx=10, pady=5)
    btn_prev.pack(side="left")
    btn_next.pack(side="right")
    update_calendar_display()
    return calendar_frame

# Обновление календаря
def update_calendar_view():
    for widget in calendar_window_frame.winfo_children():
        widget.destroy()
    create_calendar_grid(calendar_window_frame)

# Выбор эмодзи
def select_emoji_window(date_str):
    emoji_window = tk.Toplevel(root)
    emoji_window.title(f"Выберите эмодзи для {date_str}")
    emoji_window.geometry("400x250")
    emoji_window.grab_set()
    tk.Label(emoji_window, text="Выберите эмодзи:", font=(FONT_FAMILY, FONT_SIZE_HEADER)).pack(pady=10)
    frame = tk.Frame(emoji_window)
    frame.pack()
    emojis_per_row = 5
    for idx, (emotion, info) in enumerate(EMOTIONS.items()):
        row = idx // emojis_per_row
        col = idx % emojis_per_row
        btn = tk.Button(frame, text=info["emoji"], font=("Arial", 18), width=3, height=1,
                        command=lambda e=emotion, d=date_str, w=emoji_window: apply_emoji(e, d, w))
        btn.grid(row=row, column=col, padx=5, pady=5)
    tk.Button(emoji_window, text="Отмена", fg="black", bg="white", command=emoji_window.destroy).pack(pady=10)

def apply_emoji(emotion, date_str, window):
    data = load_data()
    note = data.get(date_str, {}).get("note", "")
    data[date_str] = {"emotion": emotion, "note": note}
    save_data(data)
    update_calendar_view()
    window.destroy()
    print(f"Эмодзи изменён: {date_str} → {emotion}")

# Графики
def show_charts_with_pie():
    data = load_data()
    if not data:
        messagebox.showinfo("Нет данных", "Нет записей для отображения графиков.")
        return
    emotions = [info["emotion"] for info in data.values()]
    emotion_count = Counter(emotions)
    total = len(emotions)
    labels = list(emotion_count.keys())
    counts = list(emotion_count.values())
    percentages = [f"{(count / total * 100):.1f}%" for count in counts]
    colors = ['#FFD700', '#4682B4', '#9370DB', '#B22222', '#8A2BE2',
              '#556B2F', '#87CEEB', '#FFA500', '#2E8B57', '#A9A9A9']
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    axes[0].bar(labels, counts, color=colors[:len(labels)], edgecolor='black', linewidth=1.2)
    axes[0].tick_params(axis='x', rotation=45, labelsize=10)
    axes[0].set_ylabel("Количество", fontsize=12)
    axes[0].set_xlabel("Эмоции", fontsize=12)
    axes[0].grid(True, linestyle='--', alpha=0.6)
    wedges, texts = axes[1].pie(counts, startangle=90, colors=colors[:len(labels)],
                               wedgeprops=dict(width=0.4))
    axes[1].axis('equal')
    legend_labels = [f"{label}: {percent}" for label, percent in zip(labels, percentages)]
    axes[1].legend(wedges, legend_labels, title="Эмоции", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.tight_layout()
    chart_window = tk.Toplevel(root)
    chart_window.title("Аналитика эмоций")
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Анализ за месяц
def show_month_analytics(month_str, year_str):
    try:
        month = int(month_str.split(" - ")[0])  # Извлекаем номер месяца
        year = int(year_str)
    except ValueError:
        messagebox.showerror("Ошибка", "Некорректный месяц или год")
        return
    data = load_data()
    if not data:
        messagebox.showinfo("Нет данных", "Нет записей для анализа.")
        return
    filtered = {}
    for date, info in data.items():
        y, m, d = date.split("-")
        if int(m) == month and int(y) == year:
            filtered[date] = info
    if not filtered:
        messagebox.showinfo("Нет данных", f"Нет записей за {month}.{year}")
        return
    emotions = [info["emotion"] for info in filtered.values()]
    emotion_count = Counter(emotions)
    top_emotion = max(emotion_count, key=emotion_count.get)
    analytics_window = tk.Toplevel(root)
    analytics_window.title(f"Аналитика за {month}.{year}")
    tk.Label(analytics_window, text=f"Самая частая эмоция за {month}.{year}:", font=(FONT_FAMILY, FONT_SIZE_HEADER)).pack(pady=10)
    tk.Label(analytics_window, text=top_emotion, font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold")).pack(pady=10)
    for emotion, count in emotion_count.items():
        tk.Label(analytics_window, text=f"{emotion}: {count} раз", font=(FONT_FAMILY, FONT_SIZE_NORMAL)).pack()

# Экспорт в Excel
def export_to_excel():
    data = load_data()
    if not data:
        return
    df = pd.DataFrame.from_dict(data, orient='index').reset_index()
    df.columns = ['Дата', 'Эмоция', 'Заметка']
    df.to_excel("emotions_export.xlsx", index=False)
    messagebox.showinfo("Экспорт", "Данные успешно экспортированы в Excel.")

# === Функция генерации промта для ИИ с полной статистикой ===
def generate_ai_prompt():
    try:
        df = pd.read_excel("emotions_export.xlsx")
    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Файл Excel не найден. Сначала выполните экспорт.")
        return

    if df.empty:
        messagebox.showinfo("Нет данных", "Файл пуст. Нет данных для анализа.")
        return

    df['Дата'] = pd.to_datetime(df['Дата'])
    df['Месяц'] = df['Дата'].dt.to_period('M')

    total_days = len(df)
    emotion_counts = df['Эмоция'].value_counts()
    top_emotions = emotion_counts.head(3)
    emotion_percentages = (emotion_counts / total_days * 100).round(1)
    stress_days = df[df['Эмоция'].isin(['Страх', 'Злость', 'Волнение'])]
    stress_ratio = f"{len(stress_days)} из {total_days} дней ({len(stress_days)/total_days*100:.1f}%)"
    most_common_notes = df['Заметка'].dropna().value_counts().head(3).index.tolist()

    prompt = (
        "Я школьник, который готовится к экзаменам и вёл дневник эмоций. Ниже — полная статистика:\n\n"
        f"📊 Общее количество дней наблюдений: {total_days} дней\n"
        f"💥 Топ-3 эмоции:\n"
        f"1. {top_emotions.index[0]} — {top_emotions.iloc[0]} раз ({emotion_percentages[top_emotions.index[0]]}%)\n"
        f"2. {top_emotions.index[1]} — {top_emotions.iloc[1]} раз ({emotion_percentages[top_emotions.index[1]]}%)\n"
        f"3. {top_emotions.index[2]} — {top_emotions.iloc[2]} раз ({emotion_percentages[top_emotions.index[2]]}%)\n\n"
        f"⚠️ Стрессовые дни (страх, злость, волнение): {stress_ratio}\n"
        f"📝 Наиболее частые заметки:\n"
        f"1. '{most_common_notes[0]}'\n"
        f"2. '{most_common_notes[1]}'\n"
        f"3. '{most_common_notes[2]}'\n\n"
        f"📈 Динамика эмоций по месяцам:\n"
    )

    monthly_trend = df.groupby('Месяц')['Эмоция'].value_counts().unstack(fill_value=0)
    for month in monthly_trend.index:
        prompt += f"- {month}:\n"
        for emotion in monthly_trend.columns:
            count = monthly_trend.loc[month, emotion]
            if count > 0:
                prompt += f"  • {emotion}: {count} раз\n"

    prompt += (
        "\nПроанализируй моё эмоциональное состояние. "
        "Оцени, как часто я испытываю стрессовые эмоции, "
        "как это влияет на подготовку к экзаменам, "
        "и предложи конкретные рекомендации:\n"
        "- Как снизить уровень тревожности и стресса\n"
        "- Как улучшить концентрацию и уверенность в себе\n"
        "- Какие техники помогут сохранять спокойствие\n"
        "- Какие дни или события чаще всего вызывают напряжение\n"
        "- Какие эмоции положительно влияют на продуктивность"
    )

    prompt_window = tk.Toplevel(root)
    prompt_window.title("AI Промт с полной статистикой")
    prompt_window.geometry("800x600")

    text_area = tk.Text(prompt_window, wrap="word", font=(FONT_FAMILY, FONT_SIZE_NORMAL))
    text_area.pack(padx=10, pady=10, fill="both", expand=True)
    text_area.insert("1.0", prompt)

    def copy_to_clipboard():
        root.clipboard_clear()
        root.clipboard_append(prompt)
        messagebox.showinfo("Копирование", "Промт скопирован в буфер обмена!")

    btn_copy = tk.Button(prompt_window, text="📋 Копировать в буфер", command=copy_to_clipboard,
                         font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=COLOR_PRIMARY, fg="black")
    btn_copy.pack(pady=5)

# === GUI ===
root = tk.Tk()
root.title("Календарь эмоций")
root.geometry("1200x900")
root.configure(bg=COLOR_BG)
style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", background=COLOR_BUTTON_BG, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
style.map("TButton", background=[('active', COLOR_BUTTON_HOVER)])

# Основные контейнеры
main_frame = tk.Frame(root, bg=COLOR_BG)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)
left_frame = tk.Frame(main_frame, bg=COLOR_BG)
right_frame = tk.Frame(main_frame, bg=COLOR_BG)
left_frame.pack(side="left", fill="both", expand=False)
right_frame.pack(side="right", fill="both", expand=True)

# Краткая подсказка
tooltip_text = (
    "Что ты чувствуешь сегодня?\n"
    "выбери эмодзи – shift + клик на день \n"
    "удалить запись – двойной клик"
)
tooltip_label = tk.Label(left_frame, text=tooltip_text, font=(FONT_FAMILY, 18), fg="#333", bg="#F9FAFB", justify="left",
                         padx=10, pady=5, wraplength=400)
tooltip_label.pack(pady=10, fill="x")

# Календарь
calendar_window_frame = tk.Frame(left_frame, bg=COLOR_BG)
calendar_window_frame.pack(pady=10)
update_calendar_view()

# --- Правая часть ---
tooltip_text = (
    "Как ввести дополнительную информацию?\n"
    "1. кликните на нужный день\n"
    "2. выберите эмоцию из списка\n"
    "3. можете написать, как прошёл день\n"
    "4. нажмите кнопку сохранить"
)
tooltip_label = tk.Label(right_frame, text=tooltip_text, font=(FONT_FAMILY, 18), fg="#333", bg="#F9FAFB", justify="left",
                         padx=10, pady=5, wraplength=400)
tooltip_label.pack(pady=10, fill="x")

# Выбор даты
label_selected_date = tk.Label(right_frame, text="Дата не выбрана", font=(FONT_FAMILY, FONT_SIZE_NORMAL), fg="blue",
                               bg=COLOR_BG)
label_selected_date.pack(pady=5)

# Выбор эмоции
tk.Label(right_frame, text="список эмоций", font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=COLOR_BG).pack()
combo_emotion = ttk.Combobox(right_frame, values=list(EMOTIONS.keys()), font=(FONT_FAMILY, FONT_SIZE_NORMAL))
combo_emotion.pack(pady=5)
description_var = StringVar()
label_description = tk.Label(right_frame, textvariable=description_var, wraplength=500, justify="left",
                             font=(FONT_FAMILY, FONT_SIZE_NORMAL), fg="#555", bg=COLOR_BG)
label_description.pack(pady=5)
combo_emotion.bind("<<ComboboxSelected>>", lambda e: description_var.set(
    EMOTIONS.get(combo_emotion.get(), {}).get("desc", "")))

# Поле для заметок
tk.Label(right_frame, text="Как прошёл день?", font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=COLOR_BG).pack(pady=5)
note_text = tk.Text(right_frame, height=5, width=30, wrap="word", font=(FONT_FAMILY, FONT_SIZE_NORMAL))
note_text.pack(pady=5)

# Кнопка сохранения
btn_save = tk.Button(right_frame, text="💾 Сохранить", command=save_emotion,
                     font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                     bg=COLOR_PRIMARY, fg="black", bd=0, padx=10, pady=6)
btn_save.pack(pady=10)

# Анализ за месяц
analytics_frame = tk.Frame(right_frame, bg=COLOR_BG)
analytics_frame.pack(pady=10)
month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
               "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
month_values = [f"{str(i + 1).zfill(2)} - {month_names[i]}" for i in range(12)]
combo_month = ttk.Combobox(analytics_frame, values=month_values, width=15, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
current_month = datetime.now().month
combo_month.set(f"{str(current_month).zfill(2)} - {month_names[current_month - 1]}")
combo_month.pack(side="left", padx=5)
year_values = [str(year) for year in range(2020, 2031)]
combo_year = ttk.Combobox(analytics_frame, values=year_values, width=5, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
combo_year.set(str(datetime.now().year))
combo_year.pack(side="left", padx=5)
btn_show_month_analytics = tk.Button(analytics_frame, text="📊 Показать аналитику",
                                    command=lambda: show_month_analytics(combo_month.get(), combo_year.get()),
                                    font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=COLOR_BUTTON_BG,
                                    activebackground=COLOR_BUTTON_HOVER, bd=0, padx=10, pady=5)
btn_show_month_analytics.pack(side="left", padx=5)

# Дополнительные кнопки
btn_chart = tk.Button(right_frame, text="📈 Показать графики", command=show_charts_with_pie,
                      font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=COLOR_BUTTON_BG,
                      activebackground=COLOR_BUTTON_HOVER, bd=0, padx=10, pady=5)
btn_chart.pack(pady=5)
btn_export = tk.Button(right_frame, text="📁 Экспорт в Excel", command=export_to_excel,
                       font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=COLOR_BUTTON_BG,
                       activebackground=COLOR_BUTTON_HOVER, bd=0, padx=10, pady=5)
btn_export.pack(pady=5)

# === Новая кнопка: Сформулировать запрос для ИИ ===
btn_ai_prompt = tk.Button(right_frame, text="🤖 Сформулировать запрос для ИИ",
                          command=generate_ai_prompt,
                          font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg="#A855F7", fg="black", bd=0, padx=10, pady=5)
btn_ai_prompt.pack(pady=5)

# Запуск
root.mainloop()