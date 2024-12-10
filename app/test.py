from card_fetcher import fetch_card_info
from deck_parser import parse_decklist
from simulation import MTGSimulation


def load_test_decklist():
    """
    Loads the test decklist from decklist.txt in the root directory.
    """
    try:
        with open("decklist.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print("Error: decklist.txt not found.")
        return ""


def run_simulations(enriched_decklist, num_simulations=10):
    """
    Runs the simulation multiple times and calculates the average benchmark score.
    """
    total_score = 0
    total_turns = 0

    for i in range(num_simulations):
        simulation = MTGSimulation(enriched_decklist)
        result = simulation.simulate_game()
        total_score += result["benchmark_score"]
        total_turns += result["turns"]
        print(f"Simulation {i + 1}: Benchmark Score = {result['benchmark_score']}, Turns = {result['turns']}")

    avg_score = total_score / num_simulations
    avg_turns = total_turns / num_simulations
    return avg_score, avg_turns


# Load and parse the decklist
decklist_content = load_test_decklist()
parsed_decklist = parse_decklist(decklist_content)

# Enrich the parsed decklist with card information
enriched_decklist = []
for card in parsed_decklist:
    card_info = fetch_card_info(card["name"])
    if card_info:
        enriched_card = {
            "quantity": card["quantity"],
            "name": card["name"],
            "set_code": card["set_code"],
            "collector_number": card["collector_number"],
            "type": card_info.get("type", "Unknown"),
            "mana_cost": card_info.get("mana_cost", ""),
            "cmc": card_info.get("cmc", 0),
            "produced_mana": card_info.get("produced_mana", [])
        }
        enriched_decklist.append(enriched_card)
        print(f"Enriched card: {enriched_card}")
    else:
        print(f"Warning: Could not fetch info for card '{card['name']}'")
        enriched_decklist.append(card)  # Add the card without enrichment

# Run simulations and calculate average benchmark score
average_score, average_turns = run_simulations(enriched_decklist, num_simulations=10)
print(f"Average Benchmark Score: {average_score}")
print(f"Average Turns: {average_turns}")
