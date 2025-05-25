# config.py

# Czy aplikacja działa w trybie symulacji (brak fizycznego ESP32)
SIMULATE = True

# Jeśli SIMULATE = False, użyj poniższych ustawień do połączenia przez UART
SERIAL_PORT = "COM3"        # lub "/dev/ttyUSB0" na Linuxie
BAUDRATE = 115200           # Baudrate dla ESP32

# Częstotliwość próbkowania danych (w milisekundach)
SAMPLE_INTERVAL_MS = 50     # 20 Hz (dla wykresu EKG)

# Liczba punktów na wykresie (bufor)
BUFFER_SIZE = 500

# Zakres wartości EKG (dla normalizacji/analizy)
ECG_MIN = 0
ECG_MAX = 1023
