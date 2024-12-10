from app.simulation import MTGSimulation
from app.deck_parser import parse_decklist
from concurrent.futures import ProcessPoolExecutor

def run_benchmark(decklist, iterations=100):
    """Runs multiple simulations and aggregates results."""
    results = []
    scores = []
    for _ in range(iterations):
        sim = MTGSimulation(decklist.copy())
        result = sim.simulate_game()
        results.append(result)
        scores.append(result["benchmark_score"])

    avg_score = sum(scores) / len(scores)

    return {
        "iterations": iterations,
        "avg_score": avg_score,
        "max_score": max(scores),
        "min_score": min(scores),
        "details": results
    }
