import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
import calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter

# Путь к файлу данных
DATA_FILE = "math_tracker.json"

# Темы математики
TOPICS = ["векторы и координаты", "четырехугольники", "окружность", "треугольники", "другое"]

# Цвета и стили
FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 12
FONT_SIZE_LARGE = 14
FONT_SIZE_HEADER = 16
COLOR_BG = "#F9FAFB"
COLOR_PRIMARY = "#3B82F6"
COLOR_BUTTON_BG = "#BFDBFE"
COLOR_BUTTON_HOVER = "#93C5FD"


# === Работа с данными ===
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"history": {}}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# Глобальная переменная для хранения выбранной даты
selected_date = None


# === Сохранение времени занятия + заметка ===
def save_study_time():
    global selected_date
    topic = combo_topic.get()
    try:
        minutes = float(entry_minutes.get())
        note = entry_note.get("1.0", tk.END).strip()
        if not selected_date or not topic:
            messagebox.showwarning("Ошибка", "Выберите дату и тему.")
            return
        data = load_data()
        if selected_date not in data["history"]:
            data["history"][selected_date] = []
        data["history"][selected_date].append({
            "topic": topic,
            "minutes": minutes,
            "note": note
        })
        save_data(data)
        update_calendar_view()
        clear_form()
        messagebox.showinfo("Успех", f"Добавлено {minutes} мин по '{topic}' за {selected_date}")
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректное число.")


# === Очистка формы ===
def clear_form():
    global selected_date
    selected_date = None
    label_selected_date.config(text="Дата не выбрана")
    entry_minutes.delete(0, tk.END)
    entry_note.delete("1.0", tk.END)
    combo_topic.set("")


# === Подсказки (Tooltip) ===
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
            total_minutes = 0
            notes = []
            if date_str in data["history"]:
                entries = data["history"][date_str]
                total_minutes = sum(e["minutes"] for e in entries)
                notes = [e.get("note", "") for e in entries if e.get("note", "")]
            display_text = str(int(total_minutes)) if total_minutes > 0 else ""
            lbl = tk.Label(calendar_frame, text=display_text, font=("Arial", 14), width=8, height=2,
                           relief="groove", bg="white", cursor="hand2")
            lbl.grid(row=row, column=col, padx=4, pady=4)

            tooltip_notes = "\n".join(notes[:3]) if notes else "Нет заметок"
            Tooltip(lbl, f"Дата: {date_str}\nВсего: {total_minutes} мин\nЗаметки:\n{tooltip_notes}")

            def on_click(event, d=date_str):
                global selected_date
                selected_date = d
                label_selected_date.config(text=f"Выбрана дата: {selected_date}")
                data = load_data()
                if d in data["history"]:
                    entries = data["history"][d]
                    if entries:
                        first_entry = entries[0]
                        combo_topic.set(first_entry["topic"])
                        entry_minutes.delete(0, tk.END)
                        entry_minutes.insert(tk.END, str(first_entry["minutes"]))
                        entry_note.delete("1.0", tk.END)
                        entry_note.insert(tk.END, first_entry.get("note", ""))
                    else:
                        combo_topic.set("")
                        entry_minutes.delete(0, tk.END)
                        entry_note.delete("1.0", tk.END)
                else:
                    combo_topic.set("")
                    entry_minutes.delete(0, tk.END)
                    entry_note.delete("1.0", tk.END)

            def on_double_click(event, d=date_str):
                if messagebox.askyesno("Подтверждение", f"Удалить все записи за {d}?"):
                    data = load_data()
                    if d in data["history"]:
                        del data["history"][d]
                        save_data(data)
                        update_calendar_view()

            lbl.bind("<Button-1>", on_click)
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


def update_calendar_view():
    for widget in calendar_window_frame.winfo_children():
        widget.destroy()
    create_calendar_grid(calendar_window_frame)


# === Статистика по темам (текстовая) ===
def show_statistics():
    data = load_data()
    topic_minutes = Counter()

    for entries in data["history"].values():
        for entry in entries:
            topic = entry["topic"]
            minutes = entry.get("minutes", 0)
            topic_minutes[topic] += minutes

    stats_window = tk.Toplevel(root)
    stats_window.title("Статистика по темам")
    stats_window.geometry("500x400")

    tk.Label(stats_window, text="📊 Статистика по темам",
             font=(FONT_FAMILY, FONT_SIZE_HEADER, "bold"), bg=COLOR_BG).pack(pady=10)

    stats_text = tk.Text(stats_window, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=50, height=15)
    stats_text.pack(padx=10, pady=10)

    for topic, total_minutes in topic_minutes.items():
        stats_text.insert(tk.END, f"- {topic}: {total_minutes} мин\n")

    stats_text.config(state=tk.DISABLED)


# === Круговая диаграмма ===
def show_chart():
    data = load_data()
    topic_minutes = Counter()

    for entries in data["history"].values():
        for entry in entries:
            topic = entry["topic"]
            minutes = entry.get("minutes", 0)
            topic_minutes[topic] += minutes

    labels = list(topic_minutes.keys())
    sizes = list(topic_minutes.values())

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    chart_window = tk.Toplevel(root)
    chart_window.title("Круговая диаграмма по темам")
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack()


# === Столбчатая диаграмма ===
def show_bar_chart():
    data = load_data()
    topic_minutes = Counter()

    for entries in data["history"].values():
        for entry in entries:
            topic = entry["topic"]
            minutes = entry.get("minutes", 0)
            topic_minutes[topic] += minutes

    labels = list(topic_minutes.keys())
    times = list(topic_minutes.values())

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, times, color=COLOR_PRIMARY)
    ax.set_title("Время, потраченное на темы (минуты)", fontsize=14)
    ax.set_xlabel("Темы", fontsize=12)
    ax.set_ylabel("Минуты", fontsize=12)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=10)

    plt.xticks(rotation=45, ha="right")

    chart_window = tk.Toplevel(root)
    chart_window.title("Столбчатая диаграмма по темам")
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack()


# === GUI ===
root = tk.Tk()
root.title("Календарь занятий по математике")
root.geometry("1200x800")
root.configure(bg=COLOR_BG)

main_frame = tk.Frame(root, bg=COLOR_BG)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

left_frame = tk.Frame(main_frame, bg=COLOR_BG)
right_frame = tk.Frame(main_frame, bg=COLOR_BG)
left_frame.pack(side="left", fill="both", expand=False)
right_frame.pack(side="right", fill="both", expand=True)

tooltip_text = (
    "Как использовать:\n"
    "1. Кликните на день\n"
    "2. Выберите тему и введите время\n"
    "3. Напишите заметку о занятии\n"
    "4. Нажмите 'Сохранить'\n"
    "5. Двойной клик — удалить день"
)
tooltip_label = tk.Label(left_frame, text=tooltip_text, font=(FONT_FAMILY, 18), fg="#333", bg="#F9FAFB",
                         justify="left", padx=10, pady=5, wraplength=400)
tooltip_label.pack(pady=10, fill="x")

calendar_window_frame = tk.Frame(left_frame, bg=COLOR_BG)
calendar_window_frame.pack(pady=10)

update_calendar_view()

tk.Label(right_frame, text="Выберите тему:", font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=COLOR_BG).pack()
combo_topic = ttk.Combobox(right_frame, values=TOPICS, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
combo_topic.pack(pady=5)

tk.Label(right_frame, text="Минут:", font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=COLOR_BG).pack()
entry_minutes = tk.Entry(right_frame, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
entry_minutes.pack(pady=5)

tk.Label(right_frame, text="Заметка о занятии:", font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=COLOR_BG).pack(pady=5)
entry_note = tk.Text(right_frame, height=4, width=30, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
entry_note.pack(pady=5)

btn_save = tk.Button(right_frame, text="💾 Сохранить", command=save_study_time,
                     font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                     bg=COLOR_PRIMARY, fg="black", bd=0, padx=10, pady=6)
btn_save.pack(pady=10)

label_selected_date = tk.Label(right_frame, text="Дата не выбрана", font=(FONT_FAMILY, FONT_SIZE_NORMAL), fg="blue",
                               bg=COLOR_BG)
label_selected_date.pack(pady=5)

# === Статистика и график ===
stats_button = tk.Button(right_frame, text="📈 Статистика по темам", command=show_statistics,
                         font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=COLOR_BUTTON_BG,
                         activebackground=COLOR_BUTTON_HOVER, bd=0, padx=10, pady=5)
stats_button.pack(pady=5)

chart_button = tk.Button(right_frame, text="📊 Круговая диаграмма", command=show_chart,
                         font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=COLOR_BUTTON_BG,
                         activebackground=COLOR_BUTTON_HOVER, bd=0, padx=10, pady=5)
chart_button.pack(pady=5)

bar_chart_button = tk.Button(right_frame, text="柱 Столбчатая диаграмма", command=show_bar_chart,
                             font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=COLOR_BUTTON_BG,
                             activebackground=COLOR_BUTTON_HOVER, bd=0, padx=10, pady=5)
bar_chart_button.pack(pady=5)

root.mainloop()