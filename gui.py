from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QListWidget, QMessageBox, QInputDialog
)
from PyQt5.QtCore import QTimer, QTime
import pyqtgraph as pg
import csv
import os
import statistics

from config import SAMPLE_INTERVAL_MS, BUFFER_SIZE, SIMULATE
from reader import EKGReader
from analyzer import SignalAnalyzer
from data_logger import DataLogger
from history import list_sessions


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Monitor EKG – ESP32 + AD8232")
        self.setFixedSize(1000, 600)

        self.data = []
        self.ekg_values = []
        self.reader = EKGReader(simulate=SIMULATE)
        self.analyzer = SignalAnalyzer()
        self.logger = None

        self.measurement_running = False
        self.tryb_podgladu = False
        self.session_timer = QTime()

        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(SAMPLE_INTERVAL_MS)

    def init_ui(self):
        # Panel z wieloma wykresami
        self.plot_container = QWidget()
        self.plot_layout = QVBoxLayout()
        self.plot_container.setLayout(self.plot_layout)
        self.plot_widgets = []

        # Główny wykres (live)
        self.main_plot = pg.PlotWidget()
        self.main_plot.setYRange(0, 1023)
        self.main_plot.setTitle("Sygnał EKG (live)")
        self.main_plot.setLabel("left", "ADC Value")
        self.main_plot.setLabel("bottom", "Próbki")
        self.curve = self.main_plot.plot(pen='g')
        self.plot_layout.addWidget(self.main_plot)

        self.status_label = QLabel("Status: --")
        self.status_label.setStyleSheet("font-size: 16px; color: black")

        self.time_label = QLabel("Czas: 00:00")
        self.stats_label = QLabel("Śr: -- | Min: -- | Max: --")

        self.start_button = QPushButton("Rozpocznij pomiar")
        self.start_button.clicked.connect(self.toggle_measurement)

        self.new_button = QPushButton("Nowy pomiar")
        self.new_button.setVisible(False)
        self.new_button.clicked.connect(self.start_new_measurement)

        self.history_list = QListWidget()
        self.history_list.setFixedWidth(200)
        self.history_list_label = QLabel("Historia sesji:")
        self.history_list.itemClicked.connect(self.load_session)
        self.refresh_history()

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.plot_container)
        left_layout.addWidget(self.status_label)
        left_layout.addWidget(self.time_label)
        left_layout.addWidget(self.stats_label)
        left_layout.addWidget(self.start_button)
        left_layout.addWidget(self.new_button)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.history_list_label)
        right_layout.addWidget(self.history_list)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def toggle_measurement(self):
        if not self.measurement_running:
            self.measurement_running = True
            self.tryb_podgladu = False
            self.start_button.setText("Zatrzymaj pomiar")
            self.logger = DataLogger()
            self.data.clear()
            self.ekg_values.clear()
            self.session_timer.start()
        else:
            self.measurement_running = False
            self.start_button.setText("Rozpocznij pomiar")
            if self.logger:
                self.logger.close()
                # zapytaj o nazwę sesji
                new_name, ok = QInputDialog.getText(self, "Nazwa sesji", "Podaj nazwę sesji:")
                if ok and new_name.strip():
                    self.logger.rename_session(new_name.strip())
                self.logger = None
            self.refresh_history()

    def update_plot(self):
        if self.tryb_podgladu or not self.measurement_running:
            return

        result = self.reader.read_sample()
        if result is None:
            return

        lo_p, lo_m, ecg = result
        status = self.analyzer.analyze(lo_p, lo_m, ecg)

        self.ekg_values.append(ecg)
        self.data.append(ecg)
        if len(self.data) > BUFFER_SIZE:
            self.data.pop(0)

        self.curve.setData(self.data)

        if self.logger:
            self.logger.log(lo_p, lo_m, ecg)

        if status == "OK":
            self.status_label.setText("Status: Pomiar OK")
            self.status_label.setStyleSheet("color: green; font-size: 16px")
        elif status == "BRAK KONTAKTU":
            self.status_label.setText("Status: Brak kontaktu elektrody!")
            self.status_label.setStyleSheet("color: red; font-size: 16px")
        elif status == "BRAK SYGNAŁU":
            self.status_label.setText("Status: Sygnał nieczytelny")
            self.status_label.setStyleSheet("color: orange; font-size: 16px")
        else:
            self.status_label.setText(f"Status: {status}")

        elapsed = self.session_timer.elapsed() // 1000
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.time_label.setText(f"Czas: {minutes:02}:{seconds:02}")

        if self.ekg_values:
            avg = statistics.mean(self.ekg_values)
            mini = min(self.ekg_values)
            maxi = max(self.ekg_values)
            self.stats_label.setText(f"Śr: {avg:.1f} | Min: {mini} | Max: {maxi}")
        else:
            self.stats_label.setText("Śr: -- | Min: -- | Max: --")

    def refresh_history(self):
        self.history_list.clear()
        self.session_file_map = {}
        for label, filename in list_sessions():
            self.history_list.addItem(label)
            self.session_file_map[label] = filename

    def load_session(self, item):
        label = item.text()
        filename = self.session_file_map.get(label)
        if not filename:
            QMessageBox.warning(self, "Błąd", "Nie znaleziono pliku dla tej sesji.")
            return

        full_path = os.path.join("logs", filename)

        if not os.path.exists(full_path):
            QMessageBox.warning(self, "Błąd", f"Nie znaleziono pliku: {full_path}")
            return

        self.tryb_podgladu = True
        self.measurement_running = False
        self.start_button.setVisible(False)
        self.new_button.setVisible(True)

        ekg_values = []

        with open(full_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    value = int(row['EKG'])
                    ekg_values.append(value)
                except:
                    continue

        if not ekg_values:
            QMessageBox.information(self, "Brak danych", "Ten plik nie zawiera danych EKG.")
            return

        self.clear_plot_area()
        self.plot_widgets = []

        num_segments = 5
        segment_size = 250
        total = len(ekg_values)
        step = max(1, (total - segment_size) // (num_segments - 1))

        for i in range(num_segments):
            start = i * step
            end = start + segment_size
            segment = ekg_values[start:end]

            plot = pg.PlotWidget()
            plot.setYRange(0, 1023)
            plot.setTitle(f"Wykres {i+1}: próbki {start}–{end}")
            plot.setLabel("bottom", "Próbki")
            plot.plot(segment, pen='b')

            self.plot_layout.addWidget(plot)
            self.plot_widgets.append(plot)

        self.status_label.setText(f"Podgląd sesji: {filename}")
        avg = statistics.mean(segment)
        mini = min(segment)
        maxi = max(segment)
        self.stats_label.setText(f"Śr: {avg:.1f} | Min: {mini} | Max: {maxi}")
        self.time_label.setText("Czas: --")

    def start_new_measurement(self):
        self.tryb_podgladu = False
        self.start_button.setVisible(True)
        self.new_button.setVisible(False)
        self.data.clear()
        self.ekg_values.clear()
        self.clear_plot_area()
        self.curve = self.main_plot.plot(pen='g')  # nowa linia pomiarowa
        self.status_label.setText("Status: --")
        self.time_label.setText("Czas: 00:00")
        self.stats_label.setText("Śr: -- | Min: -- | Max: --")

    def clear_plot_area(self):
        for i in reversed(range(self.plot_layout.count())):
            widget = self.plot_layout.itemAt(i).widget()
            if widget:
                self.plot_layout.removeWidget(widget)
                widget.setParent(None)
