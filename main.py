import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
from datetime import datetime
import os

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Файл для хранения истории
        self.history_file = "password_history.json"
        self.history = []  # Список словарей: {"password": str, "date": str, "length": int}

        # Загрузка истории из файла
        self.load_history()

        # Создание интерфейса
        self.create_widgets()

        # Обновление таблицы истории
        self.update_history_table()

    def create_widgets(self):
        # Основной фрейм настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)

        # Длина пароля
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.length_var = tk.StringVar(value="12")
        self.length_entry = ttk.Entry(settings_frame, textvariable=self.length_var, width=10)
        self.length_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(settings_frame, text="(от 4 до 128)").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)

        # Чекбоксы для типов символов
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_punctuation = tk.BooleanVar(value=False)

        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$...)", variable=self.use_punctuation).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)

        # Кнопка генерации
        self.generate_btn = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_btn.grid(row=2, column=0, columnspan=3, pady=10)

        # Поле для отображения сгенерированного пароля
        password_frame = ttk.LabelFrame(self.root, text="Сгенерированный пароль", padding=10)
        password_frame.pack(fill=tk.X, padx=10, pady=5)

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, font=("Courier", 12), state="readonly")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.copy_btn = ttk.Button(password_frame, text="Копировать", command=self.copy_to_clipboard)
        self.copy_btn.pack(side=tk.RIGHT)

        # Таблица истории
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Создание Treeview с прокруткой
        columns = ("password", "date", "length")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        self.tree.heading("password", text="Пароль")
        self.tree.heading("date", text="Дата и время")
        self.tree.heading("length", text="Длина")
        self.tree.column("password", width=300)
        self.tree.column("date", width=150)
        self.tree.column("length", width=80)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки управления историей
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        self.clear_history_btn = ttk.Button(control_frame, text="Очистить историю", command=self.clear_history)
        self.clear_history_btn.pack(side=tk.LEFT, padx=5)

        self.delete_selected_btn = ttk.Button(control_frame, text="Удалить выбранный", command=self.delete_selected)
        self.delete_selected_btn.pack(side=tk.LEFT, padx=5)

    def get_character_set(self):
        """Возвращает список символов на основе выбранных чекбоксов и список категорий."""
        chars = []
        categories = []
        if self.use_digits.get():
            chars.extend(string.digits)
            categories.append(string.digits)
        if self.use_letters.get():
            chars.extend(string.ascii_letters)
            categories.append(string.ascii_letters)
        if self.use_punctuation.get():
            chars.extend(string.punctuation)
            categories.append(string.punctuation)
        return chars, categories

    def generate_password(self):
        """Генерация пароля с гарантией наличия всех выбранных типов символов."""
        # Проверка длины
        try:
            length = int(self.length_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Длина пароля должна быть целым числом.")
            return

        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля - 4 символа.")
            return
        if length > 128:
            messagebox.showerror("Ошибка", "Максимальная длина пароля - 128 символов.")
            return

        # Проверка, что выбран хотя бы один тип символов
        chars, categories = self.get_character_set()
        if not chars:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов.")
            return

        # Гарантия наличия всех выбранных категорий
        if len(categories) > length:
            messagebox.showerror("Ошибка", f"Длина пароля не может быть меньше количества выбранных категорий ({len(categories)}).")
            return

        # Генерация пароля
        password = []
        # Добавляем по одному символу из каждой выбранной категории
        for cat in categories:
            password.append(random.choice(cat))
        # Заполняем оставшиеся позиции случайными символами из объединённого набора
        remaining = length - len(categories)
        if remaining > 0:
            password.extend(random.choices(chars, k=remaining))
        # Перемешиваем итоговый список
        random.shuffle(password)
        password_str = ''.join(password)

        # Отображение пароля
        self.password_var.set(password_str)

        # Добавление в историю
        self.add_to_history(password_str, length)

    def add_to_history(self, password, length):
        """Добавляет пароль в историю (в начало) и сохраняет в JSON."""
        record = {
            "password": password,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "length": length
        }
        self.history.insert(0, record)  # Новый пароль в начало списка
        self.save_history()
        self.update_history_table()

    def load_history(self):
        """Загружает историю из JSON-файла."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.history = []
        else:
            self.history = []

    def save_history(self):
        """Сохраняет историю в JSON-файл."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def update_history_table(self):
        """Обновляет отображение таблицы истории."""
        # Очищаем текущие строки
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Добавляем записи из истории
        for record in self.history:
            self.tree.insert("", tk.END, values=(record["password"], record["date"], record["length"]))

    def clear_history(self):
        """Очищает всю историю после подтверждения."""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_table()

    def delete_selected(self):
        """Удаляет выбранную запись из истории."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления.")
            return
        # Получаем индекс выбранной записи (по порядку отображения)
        index = self.tree.index(selected[0])
        if 0 <= index < len(self.history):
            del self.history[index]
            self.save_history()
            self.update_history_table()

    def copy_to_clipboard(self):
        """Копирует текущий пароль в буфер обмена."""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена.")
        else:
            messagebox.showwarning("Внимание", "Нет пароля для копирования. Сначала сгенерируйте пароль.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()
