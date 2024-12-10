import requests

def fetch_card_info(card_name):
    """
    Fetches card information from the Scryfall API and uses the produced_mana field directly.
    :param card_name: The exact name of the card to fetch.
    :return: A dictionary containing card details like name, type, mana cost, cmc, and produced mana.
    """
    url = f"https://api.scryfall.com/cards/named?exact={card_name}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            return {
                "name": data.get("name", "Unknown"),
                "type": data.get("type_line", "Unknown"),
                "mana_cost": data.get("mana_cost", ""),
                "cmc": int(data.get("cmc", 0)),
                "oracle_text": data.get("oracle_text", ""),
                "produced_mana": data.get("produced_mana", [])
            }
        else:
            print(f"Error: Unable to fetch card '{card_name}' - {response.status_code}")
    except requests.RequestException as e:
        print(f"Request failed for card '{card_name}': {e}")
    
    # Return default values if the request fails
    return {
        "name": card_name,
        "type": "Unknown",
        "mana_cost": "",
        "cmc": -1,
        "oracle_text": "",
        "produced_mana": []
    }