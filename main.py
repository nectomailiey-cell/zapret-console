import os
import sys
import subprocess
import threading
import zipfile
import shutil
import tempfile
import urllib.request
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Установка customtkinter если отсутствует
try:
    import customtkinter as ctk
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter as ctk

# Настройка внешнего вида
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ZapretApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройки окна
        self.title("Zapret Control Panel - DPI Bypass")
        self.geometry("1100x750")
        self.minsize(900, 600)
        
        # Пути
        self.zapret_path = Path("C:/zapret_ui")
        
        # Переменные
        self.service_status = ctk.StringVar(value="🔴 Не установлен")
        self.current_strategy = ctk.StringVar(value="—")
        
        # Создаём интерфейс
        self.setup_ui()
        
        # Загрузка стратегий
        self.after(100, self.load_strategies)
        
        # Периодическая проверка статуса
        self.check_status()
        
    def setup_ui(self):
        """Создание интерфейса"""
        
        # Основной контейнер
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)  # Стратегии теперь на row 4
        
        # Верхняя панель с заголовком
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Заголовок
        title_label = ctk.CTkLabel(header_frame, text="🛡️ Zapret Control Panel", 
                                   font=ctk.CTkFont(size=28, weight="bold"),
                                   text_color="#4a9eff")
        title_label.grid(row=0, column=0, sticky="w")
        
        # Кнопки управления окном (справа)
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=1, sticky="e")
        
        # Кнопка сворачивания
        minimize_btn = ctk.CTkButton(controls_frame, text="━", width=40, height=35,
                                     font=ctk.CTkFont(size=20, weight="bold"),
                                     command=self.iconify,
                                     fg_color="#2d2d3d", hover_color="#3d3d4d")
        minimize_btn.pack(side="left", padx=3)
        
        # Кнопка закрытия
        close_btn = ctk.CTkButton(controls_frame, text="✕", width=40, height=35,
                                  font=ctk.CTkFont(size=18),
                                  command=self.quit_app,
                                  fg_color="#c13b3b", hover_color="#e04e4e")
        close_btn.pack(side="left", padx=3)
        
        # Подзаголовок
        subtitle = ctk.CTkLabel(main_frame, 
                                text="Обход DPI для Discord | YouTube | Telegram | WhatsApp | Roblox | Gemini AI",
                                font=ctk.CTkFont(size=13), 
                                text_color="gray")
        subtitle.grid(row=1, column=0, pady=(0, 15))
        
        # Статус-бар
        status_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        status_inner = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_inner.pack(pady=12, padx=15)
        
        ctk.CTkLabel(status_inner, text="📊 Статус:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(0, 10))
        self.status_label = ctk.CTkLabel(status_inner, textvariable=self.service_status, 
                                         font=ctk.CTkFont(size=14), text_color="#4a9eff")
        self.status_label.pack(side="left")
        
        ctk.CTkLabel(status_inner, text="│", font=ctk.CTkFont(size=14)).pack(side="left", padx=15)
        ctk.CTkLabel(status_inner, text="🎯 Стратегия:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(status_inner, textvariable=self.current_strategy, font=ctk.CTkFont(size=14), text_color="#a6e3a1").pack(side="left")
        
        # Панель действий
        actions_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        actions_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        
        actions_inner = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_inner.pack(pady=12, padx=15, fill="x")
        
        # Кнопки действий
        buttons = [
            ("📥 Установить Zapret", self.auto_install, "#2e7d32"),
            ("⚙️ Установить службу", self.install_service, "#1565c0"),
            ("🗑️ Удалить службу", self.remove_service, "#c62828"),
            ("⏹️ Остановить все", self.stop_zapret, "#ef6c00"),
            ("🔄 Проверить статус", self.check_status, "#2c3e50"),
        ]
        
        for text, command, color in buttons:
            btn = ctk.CTkButton(actions_inner, text=text, command=command,
                               fg_color=color, hover_color=color,
                               height=38, corner_radius=8)
            btn.pack(side="left", padx=5, expand=True, fill="x")
        
        # Раздел стратегий
        strategies_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        strategies_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        strategies_frame.grid_rowconfigure(1, weight=1)
        
        # Заголовок секции
        strategies_header = ctk.CTkFrame(strategies_frame, fg_color="transparent")
        strategies_header.pack(fill="x", padx=15, pady=(12, 8))
        
        ctk.CTkLabel(strategies_header, text="🎯 Стратегии обхода", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkLabel(strategies_header, text="Выберите стратегию для запуска", 
                     font=ctk.CTkFont(size=11), text_color="gray").pack(side="left", padx=(15, 0))
        
        # Scrollable фрейм для кнопок
        self.strategies_container = ctk.CTkScrollableFrame(strategies_frame, fg_color="transparent")
        self.strategies_container.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        
        # Утилиты
        utils_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        utils_frame.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        
        utils_inner = ctk.CTkFrame(utils_frame, fg_color="transparent")
        utils_inner.pack(pady=12, padx=15, fill="x")
        
        utils_buttons = [
            ("🌐 Обновить Hosts", self.update_hosts, "#1565c0"),
            ("📡 Обновить IPSet", self.update_ipset, "#2e7d32"),
            ("🔍 Запуск диагностики", self.run_diagnostics, "#ef6c00"),
            ("🎮 Game Filter", self.toggle_game_filter, "#6a1b9a"),
        ]
        
        for text, command, color in utils_buttons:
            btn = ctk.CTkButton(utils_inner, text=text, command=command,
                               fg_color=color, hover_color=color,
                               height=35, corner_radius=8)
            btn.pack(side="left", padx=8, expand=True, fill="x")
        
        # Лог сообщений
        log_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        log_frame.grid(row=6, column=0, sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        
        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill="x", padx=15, pady=(12, 8))
        
        ctk.CTkLabel(log_header, text="📝 Консоль событий", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        
        clear_log_btn = ctk.CTkButton(log_header, text="Очистить лог", command=self.clear_log,
                                      width=120, height=32, fg_color="#2d2d3d", hover_color="#3d3d4d")
        clear_log_btn.pack(side="right")
        
        # Текстовое поле для лога
        self.log_text = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(size=11, family="Consolas"),
                                       corner_radius=8, fg_color="#1a1a2a")
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        
        # Статус-бар внизу
        status_bar = ctk.CTkFrame(main_frame, height=35, corner_radius=8, fg_color="#2d2d3d")
        status_bar.grid(row=7, column=0, sticky="ew", pady=(5, 0))
        
        self.status_bar_label = ctk.CTkLabel(status_bar, text="✅ Готов к работе", font=ctk.CTkFont(size=12))
        self.status_bar_label.pack(side="left", padx=15)
        
        version_label = ctk.CTkLabel(status_bar, text="v2.1 | Flowseal/zapret-discord-youtube", font=ctk.CTkFont(size=11))
        version_label.pack(side="right", padx=15)
        
        # Приветствие
        self.log("🚀 Zapret Control Panel запущен")
        self.log("💡 Для полной работы рекомендуется запускать от имени администратора")
        
        if not self.is_admin():
            self.log("⚠️ Внимание: программа запущена без прав администратора!", "warning")
    
    def is_admin(self):
        """Проверка прав администратора"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def log(self, message, level="info"):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }
        
        icon = icons.get(level, "📌")
        log_entry = f"[{timestamp}] {icon} {message}\n"
        
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
        self.status_bar_label.configure(text=f"{icon} {message[:60]}")
    
    def auto_install(self):
        """Автоматическая установка zapret"""
        def install():
            try:
                self.log("📥 Начинаю установку zapret...")
                
                if self.zapret_path.exists():
                    self.log("🗑️ Удаляю старую версию...")
                    shutil.rmtree(self.zapret_path)
                
                self.zapret_path.mkdir(parents=True)
                
                zip_path = self.zapret_path / "zapret.zip"
                
                self.log("🌐 Скачиваю последнюю версию...")
                url = "https://github.com/Flowseal/zapret-discord-youtube/releases/download/1.9.8b/zapret-discord-youtube-1.9.8b.zip"
                
                # Скачивание с прогрессом
                urllib.request.urlretrieve(url, zip_path)
                
                self.log("📦 Распаковываю архив...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.zapret_path)
                
                zip_path.unlink()
                
                self.log("✅ Установка успешно завершена!", "success")
                self.load_strategies()
                self.service_status.set("🟢 Готов к работе")
                
            except Exception as e:
                self.log(f"❌ Ошибка установки: {str(e)}", "error")
        
        threading.Thread(target=install, daemon=True).start()
    
    def load_strategies(self):
        """Загрузка списка стратегий"""
        # Очищаем контейнер
        for widget in self.strategies_container.winfo_children():
            widget.destroy()
        
        if not self.zapret_path.exists():
            no_zapret = ctk.CTkLabel(self.strategies_container, 
                                     text="⚠️ Zapret не установлен\nНажмите 'Установить Zapret' для начала работы",
                                     font=ctk.CTkFont(size=14))
            no_zapret.pack(pady=40)
            return
        
        # Поиск .bat файлов стратегий
        bat_files = list(self.zapret_path.glob("general*.bat"))
        
        if not bat_files:
            no_files = ctk.CTkLabel(self.strategies_container,
                                    text="📂 Стратегии не найдены\nПопробуйте переустановить Zapret",
                                    font=ctk.CTkFont(size=14))
            no_files.pack(pady=40)
            return
        
        # Группировка стратегий
        recommended = []
        alt_strategies = []
        experimental = []
        
        for bat in bat_files:
            name = bat.name.replace(".bat", "")
            if "ALT" in name:
                alt_strategies.append(bat)
            elif "SIMPLE" in name or "FAKE" in name:
                recommended.append(bat)
            else:
                experimental.append(bat)
        
        row = 0
        
        # Рекомендуемые
        if recommended:
            cat_label = ctk.CTkLabel(self.strategies_container, text="⭐ Рекомендуемые стратегии", 
                                     font=ctk.CTkFont(size=13, weight="bold"),
                                     text_color="#4a9eff")
            cat_label.grid(row=row, column=0, columnspan=3, sticky="w", pady=(10, 5))
            row += 1
            
            col = 0
            for bat in recommended:
                btn = ctk.CTkButton(self.strategies_container, 
                                   text=f"▶ {bat.name.replace('.bat', '')[:40]}",
                                   command=lambda f=bat: self.run_strategy(f),
                                   height=38)
                btn.grid(row=row, column=col, padx=5, pady=3, sticky="ew")
                col += 1
                if col >= 2:
                    col = 0
                    row += 1
            if col != 0:
                row += 1
        
        # Альтернативные
        if alt_strategies:
            cat_label = ctk.CTkLabel(self.strategies_container, text="🔄 Альтернативные стратегии", 
                                     font=ctk.CTkFont(size=13, weight="bold"),
                                     text_color="#ffb74d")
            cat_label.grid(row=row, column=0, columnspan=3, sticky="w", pady=(10, 5))
            row += 1
            
            col = 0
            for bat in alt_strategies:
                btn = ctk.CTkButton(self.strategies_container, 
                                   text=f"▶ {bat.name.replace('.bat', '')[:40]}",
                                   command=lambda f=bat: self.run_strategy(f),
                                   height=38)
                btn.grid(row=row, column=col, padx=5, pady=3, sticky="ew")
                col += 1
                if col >= 2:
                    col = 0
                    row += 1
            if col != 0:
                row += 1
        
        # Экспериментальные
        if experimental:
            cat_label = ctk.CTkLabel(self.strategies_container, text="🧪 Экспериментальные", 
                                     font=ctk.CTkFont(size=13, weight="bold"),
                                     text_color="#a6e3a1")
            cat_label.grid(row=row, column=0, columnspan=3, sticky="w", pady=(10, 5))
            row += 1
            
            col = 0
            for bat in experimental[:6]:  # Ограничиваем количество
                btn = ctk.CTkButton(self.strategies_container, 
                                   text=f"▶ {bat.name.replace('.bat', '')[:40]}",
                                   command=lambda f=bat: self.run_strategy(f),
                                   height=38)
                btn.grid(row=row, column=col, padx=5, pady=3, sticky="ew")
                col += 1
                if col >= 2:
                    col = 0
                    row += 1
        
        self.log(f"📋 Загружено {len(bat_files)} стратегий", "success")
    
    def run_strategy(self, bat_file):
        """Запуск выбранной стратегии"""
        try:
            name = bat_file.name.replace(".bat", "")
            self.log(f"▶️ Запуск стратегии: {name}")
            self.current_strategy.set(name[:40])
            
            # Запускаем в отдельном процессе
            subprocess.Popen([str(bat_file)], cwd=str(self.zapret_path), shell=True)
            self.service_status.set("🟢 Активен")
            self.log(f"✅ Стратегия '{name}' запущена", "success")
        except Exception as e:
            self.log(f"❌ Ошибка запуска: {str(e)}", "error")
    
    def install_service(self):
        """Установка службы Windows"""
        if not self.zapret_path.exists():
            self.log("❌ Сначала установите Zapret!", "error")
            return
        self.log("⚙️ Запуск установки службы...")
        subprocess.Popen([str(self.zapret_path / "service.bat")], shell=True)
    
    def remove_service(self):
        """Удаление службы"""
        if not self.zapret_path.exists():
            return
        self.log("🗑️ Запуск удаления службы...")
        subprocess.Popen([str(self.zapret_path / "service.bat")], shell=True)
    
    def stop_zapret(self):
        """Остановка всех процессов zapret"""
        try:
            self.log("⏹️ Останавливаю zapret...")
            os.system("taskkill /f /im winws.exe 2>nul")
            os.system("taskkill /f /im winws64.exe 2>nul")
            self.service_status.set("🔴 Остановлен")
            self.current_strategy.set("—")
            self.log("✅ Zapret остановлен", "success")
        except Exception as e:
            self.log(f"❌ Ошибка: {str(e)}", "error")
    
    def update_hosts(self):
        self.log("🌐 Запуск обновления hosts файла...")
        if self.zapret_path.exists():
            subprocess.Popen([str(self.zapret_path / "service.bat")], shell=True)
    
    def update_ipset(self):
        self.log("📡 Обновление IPSet списка...")
        if self.zapret_path.exists():
            subprocess.Popen([str(self.zapret_path / "service.bat")], shell=True)
    
    def run_diagnostics(self):
        self.log("🔍 Запуск диагностики...")
        if self.zapret_path.exists():
            subprocess.Popen([str(self.zapret_path / "service.bat")], shell=True)
    
    def toggle_game_filter(self):
        self.log("🎮 Переключение Game Filter...")
        if self.zapret_path.exists():
            subprocess.Popen([str(self.zapret_path / "service.bat")], shell=True)
    
    def check_status(self):
        """Периодическая проверка статуса"""
        def check():
            try:
                result = subprocess.run(["tasklist", "/fi", "imagename eq winws.exe"], 
                                       capture_output=True, text=True, shell=True)
                if "winws.exe" in result.stdout:
                    if self.service_status.get() != "🟢 Активен":
                        self.service_status.set("🟢 Активен")
                else:
                    if self.service_status.get() != "🔴 Не активен" and self.service_status.get() != "🔴 Не установлен":
                        self.service_status.set("🔴 Не активен")
            except:
                pass
            
            self.after(10000, self.check_status)
        
        threading.Thread(target=check, daemon=True).start()
    
    def clear_log(self):
        self.log_text.delete("1.0", "end")
        self.log("🧹 Лог очищен")
    
    def quit_app(self):
        """Безопасное закрытие приложения"""
        if messagebox.askokcancel("Выход", "Закрыть приложение?\nZapret продолжит работу в фоне.", icon='question'):
            self.destroy()
            self.quit()

# Добавляем импорт ctypes для проверки прав администратора
import ctypes

if __name__ == "__main__":
    app = ZapretApp()
    app.mainloop()
