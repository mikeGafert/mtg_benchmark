import re

def parse_decklist(decklist):
    """
    Verarbeitet eine Deckliste und gibt eine Liste von Karten mit Mengen und Informationen zurueck.
    """
    parsed_cards = []
    lines = decklist.splitlines()

    for line in lines:
        # Ignoriere Leerzeilen oder Sideboard-Einträge
        if not line.strip() or line.strip().upper().startswith("SIDEBOARD"):
            continue

        # Regulärer Ausdruck für die Kartenzeilen
        match = re.match(r"(\d+)\s(.+?)\s\((\w+)\)\s(\d+)", line)
        if match:
            quantity = int(match.group(1))
            name = match.group(2)
            set_code = match.group(3)
            collector_number = match.group(4)

            parsed_cards.append({
                "quantity": quantity,
                "name": name,
                "set_code": set_code,
                "collector_number": collector_number
            })

    return parsed_cards