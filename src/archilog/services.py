import csv
import dataclasses
import io
from archilog.models import create_entry, get_all_entries, Entry




def export_to_csv(csv_file_path=None):
    csv_file = io.StringIO() if csv_file_path is None else open(csv_file_path, "w", newline="", encoding="utf-8")


    entries = get_all_entries()

    csv_writer = csv.DictWriter(csv_file, fieldnames=[f.name for f in dataclasses.fields(Entry)])
    csv_writer.writeheader()

    for entry in entries:
        csv_writer.writerow(dataclasses.asdict(entry))

    if csv_file_path is None:
        csv_file.seek(0)  # Revenir au début pour Flask
        return csv_file
    else:
        csv_file.close()  # Fermer le fichier pour Click
        print(f"Exportation réussie vers {csv_file_path} !")
        

def import_from_csv(csv_file) -> None:
    content = csv_file.read()

    # Vérifie si on doit décoder
    if isinstance(content, bytes):
        content = content.decode("utf-8")

    file_stream = io.StringIO(content)

    csv_reader = csv.DictReader(file_stream)
    for row in csv_reader:
        create_entry(
            name=row["name"],
            amount=float(row["amount"]),
            category=row["category"]
        )
