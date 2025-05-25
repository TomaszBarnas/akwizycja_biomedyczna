import csv
import datetime
import os
import shutil

class DataLogger:
    def __init__(self, directory="logs"):
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.base_filename = f"ekg_log_{timestamp}"
        self.full_path = os.path.join(directory, self.base_filename + ".csv")

        self.file = open(self.full_path, mode='w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(["Czas", "LO+", "LO-", "EKG"])

    def log(self, lo_p, lo_m, ecg_sample):
        now = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.writer.writerow([now, lo_p, lo_m, ecg_sample])

    def close(self):
        if self.file:
            self.file.close()

    def rename_session(self, new_name):
        """Zmienia nazwę sesji i zapisuje opis do pliku .meta"""
        safe_name = "".join(c for c in new_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
        meta_filename = self.base_filename + ".meta"

        with open(os.path.join(self.directory, meta_filename), "w", encoding="utf-8") as metafile:
            metafile.write(safe_name + "\n")

        # Zmieniamy nazwę pliku CSV na coś bardziej rozpoznawalnego (opcjonalnie)
        new_csv_name = f"{safe_name}_{self.base_filename}.csv"
        new_csv_path = os.path.join(self.directory, new_csv_name)

        # Zmieniamy nazwę pliku
        try:
            os.rename(self.full_path, new_csv_path)
            self.full_path = new_csv_path
        except Exception as e:
            print(f"Błąd podczas zmiany nazwy pliku: {e}")
