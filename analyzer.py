class SignalAnalyzer:
    def __init__(self):
        # Próg poniżej którego sygnał jest uznawany za "martwy"
        self.min_valid_ecg = 10
        self.max_valid_ecg = 1013
        # W przyszłości można tu dodać analizę amplitudy, QRS, itp.

    def analyze(self, lo_p, lo_m, ecg_sample):
        # Brak kontaktu elektrody
        if lo_p == 1 or lo_m == 1:
            return "BRAK KONTAKTU"

        # Brak sygnału / zbyt niska lub zbyt wysoka wartość
        if ecg_sample < self.min_valid_ecg or ecg_sample > self.max_valid_ecg:
            return "BRAK SYGNAŁU"

        return "OK"
