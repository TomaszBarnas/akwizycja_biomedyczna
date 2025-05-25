import random
import serial
from config import SERIAL_PORT, BAUDRATE

class EKGReader:
    def __init__(self, simulate=True):
        self.simulate = simulate
        if not simulate:
            try:
                self.ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
            except Exception as e:
                print(f"Nie udało się połączyć z portem {SERIAL_PORT}: {e}")
                self.simulate = True

    def read_sample(self):
        if self.simulate:
            lo_p = random.choice([0, 1])
            lo_m = random.choice([0, 1])
            contact = (lo_p == 0 and lo_m == 0)
            ecg = random.randint(450, 580) if contact else random.randint(0, 20)
            return lo_p, lo_m, ecg

        try:
            if self.ser.in_waiting:
                line = self.ser.readline().decode().strip()
                parts = line.split(',')
                if len(parts) == 3:
                    lo_p, lo_m, ecg = map(int, parts)
                    return lo_p, lo_m, ecg
        except Exception as e:
            print(f"Błąd odczytu: {e}")
            return None
