import random
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QCalendarWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QWidget, QStackedWidget, QPushButton, QFrame, QScrollArea,
    QGridLayout, QDialog, QLineEdit, QMessageBox, QComboBox, QFileDialog, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QDateTime, QTimer, QDate, QSize
from PyQt5.QtGui import QTextCharFormat, QColor, QFont, QPixmap, QIcon

class ModernCalendarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("İnteraktif Takvim")
        self.setGeometry(100, 100, 1550, 930)
        self.main_layout = QHBoxLayout()

        self.menu_frame = QFrame()
        self.menu_frame.setStyleSheet("background-color: #f0f8ff;")
        self.menu_layout = QVBoxLayout(self.menu_frame)

        self.calendar_button = self.create_styled_button("Takvim")
        self.calendar_button.clicked.connect(self.switch_to_calendar)
        self.menu_layout.addWidget(self.calendar_button)
        self.chores_button = self.create_styled_button("Günlük İşler")
        self.menu_layout.addWidget(self.chores_button)
        self.rewards_button = self.create_styled_button("Ödüller")
        self.rewards_button.clicked.connect(self.switch_to_rewards)
        self.menu_layout.addWidget(self.rewards_button)
        self.meals_button = self.create_styled_button("Yemek Tarifleri")
        self.menu_layout.addWidget(self.meals_button)
        self.photos_button = self.create_styled_button("Fotoğraflar")
        self.photos_button.clicked.connect(self.switch_to_photos)
        self.menu_layout.addWidget(self.photos_button)
        self.menu_layout.addStretch()

        self.stacked_widget = QStackedWidget()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        self.events = {}

        # Başlangıç Ekranı
        self.start_screen = QWidget()
        self.start_layout = QVBoxLayout(self.start_screen)
        self.start_layout.setAlignment(Qt.AlignCenter)
        self.weather_label = QLabel("🌤 Güneşli 18°C")
        self.weather_label.setFont(QFont("Arial", 18))
        self.weather_label.setAlignment(Qt.AlignCenter)
        self.start_layout.addWidget(self.weather_label)
        self.date_label = QLabel(QDateTime.currentDateTime().toString("dd MMMM yyyy"))
        self.date_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.date_label.setAlignment(Qt.AlignCenter)
        self.start_layout.addWidget(self.date_label)
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 48, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.start_layout.addWidget(self.time_label)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        self.start_screen.mousePressEvent = self.switch_to_calendar
        self.stacked_widget.addWidget(self.start_screen)

        # Takvim Ekranı
        self.calendar_screen = QWidget()
        self.calendar_layout = QVBoxLayout(self.calendar_screen)
        self.event_strip_widget = QWidget()
        self.event_strip_layout = QHBoxLayout(self.event_strip_widget)
        self.event_strip_layout.setSpacing(8)
        self.event_strip_layout.setContentsMargins(0,0,0,0)
        self.calendar_layout.addWidget(self.event_strip_widget)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.currentPageChanged.connect(lambda y, m: self.update_event_strip())
        self.calendar.selectionChanged.connect(self.update_event_strip)
        self.calendar.clicked.connect(self.show_day_details)
        self.highlight_today()
        self.update_event_strip()
        self.calendar_layout.addWidget(self.calendar)
        self.stacked_widget.addWidget(self.calendar_screen)

        self.day_details_screen = QWidget()
        self.day_details_layout = QVBoxLayout(self.day_details_screen)
        self.day_label = QLabel("Gün Detayları")
        self.day_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.day_label.setAlignment(Qt.AlignCenter)
        self.day_details_layout.addWidget(self.day_label)
        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_area_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.day_details_layout.addWidget(self.scroll_area)
        self.add_event_button = self.create_styled_button("Etkinlik Ekle")
        self.add_event_button.clicked.connect(self.open_add_event_popup)
        self.day_details_layout.addWidget(self.add_event_button)
        self.stacked_widget.addWidget(self.day_details_screen)

        # Fotoğraflar ekranı
        self.photos_screen = QWidget()
        photos_layout = QVBoxLayout(self.photos_screen)
        self.photo_add_button = self.create_styled_button("Fotoğraf Ekle")
        self.photo_add_button.clicked.connect(self.add_photo)
        photos_layout.addWidget(self.photo_add_button)
        self.photos_list_widget = QListWidget()
        self.photos_list_widget.setViewMode(QListWidget.IconMode)
        self.photos_list_widget.setIconSize(QSize(140, 120))
        self.photos_list_widget.setResizeMode(QListWidget.Adjust)
        self.photos_list_widget.setSpacing(20)
        photos_layout.addWidget(self.photos_list_widget)
        self.photos = []  # Dosya yolları
        self.stacked_widget.addWidget(self.photos_screen)

        # Ödüller ekranı
        self.rewards_screen = QWidget()
        rewards_layout = QVBoxLayout(self.rewards_screen)
        self.reward_add_button = self.create_styled_button("Ödül Ekle")
        self.reward_add_button.clicked.connect(self.add_reward)
        rewards_layout.addWidget(self.reward_add_button)
        self.rewards_list_widget = QListWidget()
        self.rewards_list_widget.setSpacing(10)
        rewards_layout.addWidget(self.rewards_list_widget)
        self.rewards = []  # Ödül adları
        self.stacked_widget.addWidget(self.rewards_screen)

        self.update_main_layout(for_start_screen=True)

    def create_styled_button(self, text):
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QPushButton:pressed {
                background-color: #003E73;
            }
        """)
        return button

    def update_main_layout(self, for_start_screen=False):
        for i in reversed(range(self.main_layout.count())):
            widget = self.main_layout.itemAt(i).widget()
            if widget:
                self.main_layout.removeWidget(widget)
        if for_start_screen:
            self.main_layout.addWidget(self.stacked_widget, 1)
        else:
            self.main_layout.addWidget(self.menu_frame, 1)
            self.main_layout.addWidget(self.stacked_widget, 4)

    def update_time(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.time_label.setText(current_time)

    def highlight_today(self):
        today = QDate.currentDate()
        format = QTextCharFormat()
        format.setBackground(QColor("#FFA500"))
        format.setForeground(QColor("#FFFFFF"))
        format.setFontWeight(QFont.Bold)
        self.calendar.setDateTextFormat(today, format)

    def switch_to_calendar(self, event=None):
        self.update_main_layout(for_start_screen=False)
        self.stacked_widget.setCurrentWidget(self.calendar_screen)

    def switch_to_photos(self):
        self.update_main_layout(for_start_screen=False)
        self.stacked_widget.setCurrentWidget(self.photos_screen)

    def switch_to_rewards(self):
        self.update_main_layout(for_start_screen=False)
        self.stacked_widget.setCurrentWidget(self.rewards_screen)

    def update_event_strip(self):
        for i in reversed(range(self.event_strip_layout.count())):
            widget = self.event_strip_layout.itemAt(i).widget()
            if widget:
                self.event_strip_layout.removeWidget(widget)
                widget.deleteLater()
        cal_date = self.calendar.selectedDate()
        this_month = cal_date.month()
        this_year = cal_date.year()
        renkler = ["#b2ffb2", "#ffe4b5", "#add8e6", "#ffd6f9", "#ffb6b6", "#ffe599", "#d0e0e3"]
        renk_index = 0
        items = []
        for day_str, by_hours in sorted(self.events.items()):
            d = QDate.fromString(day_str, "yyyy-MM-dd")
            if d.month() == this_month and d.year() == this_year:
                for hour, event_list in by_hours.items():
                    for event, member in event_list:
                        items.append( (d.day(), hour, event, member) )
        items.sort()
        for (g, saat, etkinlik, kisi) in items:
            renk = renkler[renk_index % len(renkler)]
            renk_index += 1
            kart = QFrame()
            kart.setStyleSheet(f"background-color: {renk}; border-radius: 10px; border: 1.5px solid #bbb;")
            h = QHBoxLayout(kart)
            h.setContentsMargins(8, 2, 8, 2)
            lbl = QLabel(f"<b>{g}</b>  | {saat}:00 | {etkinlik} <i>({kisi})</i>")
            lbl.setFont(QFont('Arial', 12))
            h.addWidget(lbl)
            self.event_strip_layout.addWidget(kart)
        self.event_strip_layout.addStretch()

    def show_day_details(self, date):
        selected_date = date.toString("yyyy-MM-dd")
        self.day_label.setText(f"{selected_date} Tarihi için Detaylar")
        for i in reversed(range(self.scroll_layout.count())):
            child = self.scroll_layout.takeAt(i)
            if child.widget():
                child.widget().deleteLater()
        if selected_date in self.events:
            row = 0
            for hour, event_list in sorted(self.events[selected_date].items()):
                for idx, (event, member) in enumerate(event_list):
                    card = QFrame()
                    card.setFrameShape(QFrame.Box)
                    card.setStyleSheet("""
                        QFrame {
                            background-color: #e6f2ff;
                            border: 2px solid #0078D7;
                            border-radius: 12px;
                            padding: 12px;
                            margin-bottom: 8px;
                        }
                    """)
                    card_layout = QHBoxLayout(card)
                    time_icon = QLabel("🕒")
                    time_icon.setFont(QFont("Arial", 18))
                    time_label = QLabel(f"{hour}:00")
                    time_label.setFont(QFont("Arial", 16, QFont.Bold))
                    vbox = QVBoxLayout()
                    vbox.addWidget(time_icon)
                    vbox.addWidget(time_label)
                    vbox.setAlignment(Qt.AlignCenter)
                    card_layout.addLayout(vbox)
                    event_name = QLabel(f"{event}")
                    event_name.setFont(QFont("Arial", 16, QFont.Bold))
                    card_layout.addWidget(event_name, stretch=2)
                    member_icon = QLabel("👤")
                    member_icon.setFont(QFont("Arial", 18))
                    member_label = QLabel(f"{member}")
                    member_label.setFont(QFont("Arial", 14))
                    vbox2 = QVBoxLayout()
                    vbox2.addWidget(member_icon)
                    vbox2.addWidget(member_label)
                    vbox2.setAlignment(Qt.AlignCenter)
                    card_layout.addLayout(vbox2)
                    btn_layout = QVBoxLayout()
                    delete_btn = QPushButton("Sil")
                    edit_btn = QPushButton("Düzenle")
                    delete_btn.setStyleSheet("background-color: #ff5252; color: white; font-weight: bold; border-radius: 6px; padding: 4px 8px;")
                    edit_btn.setStyleSheet("background-color: #ffc107; color: black; font-weight: bold; border-radius: 6px; padding: 4px 8px;")
                    btn_layout.addWidget(edit_btn)
                    btn_layout.addWidget(delete_btn)
                    card_layout.addLayout(btn_layout)
                    def make_delete_func(hour_=hour, idx_=idx):
                        def delete_event():
                            self.events[selected_date][hour_].pop(idx_)
                            if not self.events[selected_date][hour_]:
                                del self.events[selected_date][hour_]
                            if not self.events[selected_date]:
                                del self.events[selected_date]
                            self.update_event_strip()
                            self.show_day_details(self.calendar.selectedDate())
                        return delete_event
                    delete_btn.clicked.connect(make_delete_func(hour, idx))
                    def make_edit_func(hour_=hour, idx_=idx):
                        def edit_event():
                            current_event, current_member = self.events[selected_date][hour_][idx_]
                            dialog = QDialog(self)
                            dialog.setWindowTitle("Etkinlik Düzenle")
                            layout = QVBoxLayout(dialog)
                            hour_label = QLabel("Saat (0-23):")
                            hour_input = QComboBox()
                            hour_input.addItems([str(h) for h in range(24)])
                            hour_input.setCurrentText(str(hour_))
                            layout.addWidget(hour_label)
                            layout.addWidget(hour_input)
                            event_label = QLabel("Etkinlik Adı:")
                            event_input = QLineEdit()
                            event_input.setText(current_event)
                            layout.addWidget(event_label)
                            layout.addWidget(event_input)
                            member_label = QLabel("Kişi:")
                            member_input = QLineEdit()
                            member_input.setText(current_member)
                            layout.addWidget(member_label)
                            layout.addWidget(member_input)
                            button_layout = QHBoxLayout()
                            save_button = QPushButton("Kaydet")
                            cancel_button = QPushButton("İptal")
                            button_layout.addWidget(save_button)
                            button_layout.addWidget(cancel_button)
                            layout.addLayout(button_layout)
                            def save_changes():
                                new_hour = hour_input.currentText()
                                event_name = event_input.text().strip()
                                member = member_input.text().strip()
                                if not event_name:
                                    QMessageBox.warning(dialog, "Uyarı", "Etkinlik adı boş olamaz!")
                                    return
                                if not member:
                                    QMessageBox.warning(dialog, "Uyarı", "Kişi adı boş olamaz!")
                                    return
                                self.events[selected_date][hour_].pop(idx_)
                                if not self.events[selected_date][hour_]:
                                    del self.events[selected_date][hour_]
                                if not self.events[selected_date]:
                                    del self.events[selected_date]
                                if selected_date not in self.events:
                                    self.events[selected_date] = {}
                                if new_hour not in self.events[selected_date]:
                                    self.events[selected_date][new_hour] = []
                                self.events[selected_date][new_hour].append((event_name, member))
                                dialog.accept()
                                self.show_day_details(self.calendar.selectedDate())
                                self.update_event_strip()
                            save_button.clicked.connect(save_changes)
                            cancel_button.clicked.connect(dialog.reject)
                            dialog.exec_()
                        return edit_event
                    edit_btn.clicked.connect(make_edit_func(hour, idx))
                    self.scroll_layout.addWidget(card, row, 0)
                    row += 1
        else:
            no_event_label = QLabel("Bu gün için etkinlik yok.")
            no_event_label.setFont(QFont("Arial", 14))
            self.scroll_layout.addWidget(no_event_label)
        self.stacked_widget.setCurrentWidget(self.day_details_screen)

    def open_add_event_popup(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        dialog = QDialog(self)
        dialog.setWindowTitle("Etkinlik Ekle")
        layout = QVBoxLayout(dialog)
        hour_label = QLabel("Saat (0-23):")
        hour_input = QComboBox()
        hour_input.addItems([str(h) for h in range(24)])
        layout.addWidget(hour_label)
        layout.addWidget(hour_input)
        event_label = QLabel("Etkinlik Adı:")
        event_input = QLineEdit()
        layout.addWidget(event_label)
        layout.addWidget(event_input)
        member_label = QLabel("Kişi:")
        member_input = QLineEdit()
        layout.addWidget(member_label)
        layout.addWidget(member_input)
        button_layout = QHBoxLayout()
        add_button = QPushButton("Ekle")
        cancel_button = QPushButton("İptal")
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        def add_event():
            hour = hour_input.currentText()
            event_name = event_input.text().strip()
            member = member_input.text().strip()
            if not event_name:
                QMessageBox.warning(dialog, "Uyarı", "Etkinlik adı boş olamaz!")
                return
            if not member:
                QMessageBox.warning(dialog, "Uyarı", "Kişi adı boş olamaz!")
                return
            if selected_date not in self.events:
                self.events[selected_date] = {}
            if hour not in self.events[selected_date]:
                self.events[selected_date][hour] = []
            self.events[selected_date][hour].append((event_name, member))
            dialog.accept()
            if self.stacked_widget.currentWidget() == self.day_details_screen:
                self.show_day_details(self.calendar.selectedDate())
            self.update_event_strip()
        add_button.clicked.connect(add_event)
        cancel_button.clicked.connect(dialog.reject)
        dialog.exec_()

    # ----- FOTOĞRAF İŞLEMLERİ -----
    def add_photo(self):
        file_dialog = QFileDialog(self, "Fotoğraf Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                photo_path = selected_files[0]
                self.photos.append(photo_path)
                self.display_photos()

    def display_photos(self):
        self.photos_list_widget.clear()
        for photo_path in self.photos:
            if os.path.exists(photo_path):
                item = QListWidgetItem()
                icon = QIcon(QPixmap(photo_path).scaled(140, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                item.setIcon(icon)
                item.setText(os.path.basename(photo_path))
                self.photos_list_widget.addItem(item)

    # ----- ÖDÜL İŞLEMLERİ -----
    def add_reward(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ödül Ekle")
        layout = QVBoxLayout(dialog)
        label = QLabel("Ödül Adı:")
        reward_input = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(reward_input)
        button_layout = QHBoxLayout()
        add_button = QPushButton("Ekle")
        cancel_button = QPushButton("İptal")
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        def add_it():
            name = reward_input.text().strip()
            if not name:
                QMessageBox.warning(dialog, "Uyarı", "Ödül adı boş olamaz!")
                return
            self.rewards.append(name)
            self.display_rewards()
            dialog.accept()
        add_button.clicked.connect(add_it)
        cancel_button.clicked.connect(dialog.reject)
        dialog.exec_()

    def display_rewards(self):
        self.rewards_list_widget.clear()
        for name in self.rewards:
            item = QListWidgetItem(name)
            item.setFont(QFont("Arial", 14, QFont.Bold))
            # Sil butonu eklemek için widget hack
            btn = QPushButton("Sil")
            btn.setStyleSheet("background-color: #ff5252; color: white; font-weight: bold; border-radius: 6px; padding: 4px 10px;")
            def delete_reward(n=name):
                self.rewards.remove(n)
                self.display_rewards()
            btn.clicked.connect(delete_reward)
            self.rewards_list_widget.addItem(item)
            self.rewards_list_widget.setItemWidget(item, btn)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QMessageBox
    try:
        app = QApplication([])
        window = ModernCalendarApp()
        window.show()
        app.exec_()
    except Exception as e:
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "HATA", f"Bir hata oluştu:\\n{e}")
        app.exec_()
