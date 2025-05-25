import os

def list_sessions(directory="logs"):
    """
    Zwraca listę krotek (label, filename):
    - label: to co pokazujemy użytkownikowi (nazwa nadana lub nazwa pliku)
    - filename: rzeczywista nazwa pliku CSV
    """
    if not os.path.exists(directory):
        return []

    files = [f for f in os.listdir(directory)
             if f.endswith(".csv") and f.startswith("ekg_log_") or "_" in f and "ekg_log_" in f]

    session_list = []

    for csv_file in sorted(files, reverse=True):
        base = os.path.splitext(csv_file)[0]
        meta_path = os.path.join(directory, base.split("_ekg_log_")[-1] + ".meta")
        label = csv_file  # domyślnie nazwa pliku

        if os.path.exists(os.path.join(directory, meta_path)):
            try:
                with open(os.path.join(directory, meta_path), encoding='utf-8') as f:
                    name = f.readline().strip()
                    if name:
                        label = f"{name} ({csv_file})"
            except:
                pass

        session_list.append((label, csv_file))

    return session_list
