def normalize(value, old_min, old_max, new_min, new_max):
    """Przeskaluj wartość z jednego zakresu na inny."""
    if old_max - old_min == 0:
        return new_min
    return ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

def moving_average(data, window_size=5):
    """Policz średnią kroczącą na podstawie ostatnich N próbek."""
    if len(data) < window_size:
        return sum(data) / len(data)
    return sum(data[-window_size:]) / window_size

def detect_flat_signal(data, threshold=5):
    """Sprawdź, czy sygnał jest "płaski" – niska zmienność."""
    if not data:
        return True
    return max(data) - min(data) < threshold
