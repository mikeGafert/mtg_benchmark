from flask import render_template, request
from app import app
from app.deck_parser import parse_decklist
from app.simulation import MTGSimulation
from app.benchmark import run_benchmark

def load_test_decklist():
    """
    Loads the test decklist from decklist.txt in the root directory.
    """
    try:
        with open("decklist.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "1 Plains (DDN) 81\n"  # Fallback if the test file is missing

@app.route("/")
def index():
    # Use the test decklist during development
    decklist_content = load_test_decklist()
    return render_template("index.html", decklist=decklist_content)

@app.route("/benchmark", methods=["POST"])
def benchmark():
    # Load the test decklist instead of reading from the form
    decklist_content = load_test_decklist()

    # Parse the decklist
    parsed_decklist = parse_decklist(decklist_content)

    # Prepare the deck and run the benchmark
    deck = [card for card in parsed_decklist for _ in range(card["quantity"])]
    results = run_benchmark(deck, iterations=100)

    # Render the results page
    return render_template("results.html", results=results)
