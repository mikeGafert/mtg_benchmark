import random
from itertools import combinations
import re

class MTGSimulation:
    def __init__(self, decklist):
        """
        Initializes the simulation with the given decklist.
        Each card is duplicated according to its quantity.
        """
        self.original_decklist = self.expand_decklist(decklist)  # Expand cards based on quantity
        self.decklist = []
        self.hand = []
        self.field = []
        self.mana_available = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        self.turns = 0
        self.benchmark_score = 0

    def expand_decklist(self, decklist):
        """
        Expands the decklist based on card quantity.
        """
        expanded_deck = []
        for card in decklist:
            expanded_deck.extend([card] * card["quantity"])

        print(f"Expanded to {len(expanded_deck)} cards.")
        return expanded_deck

    def start_new_round(self):
        """
        Resets the decklist and draws 7 random cards for the starting hand.
        """
        self.decklist = self.original_decklist.copy()
        random.shuffle(self.decklist)  # Shuffle the deck

        # Draw 7 cards
        self.hand = [self.decklist.pop() for _ in range(7)]

        # Reset other fields for a new round
        self.field = []
        self.mana_available = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        self.turns = 0
        self.benchmark_score = 0

        print("=== New Round ===")
        print(f"Initial Hand: {[card['name'] for card in self.hand]}")
        print(f"Initial Deck Size: {len(self.decklist)}")

    def deduct_mana(self, required_mana):
        """
        Deducts mana from the available mana pool based on the requirements.
        Returns True if successful, False otherwise.
        """
        temp_pool = self.mana_available.copy()

        for color, required in required_mana.items():
            if color not in temp_pool:
                print(f"Warning: Unknown mana type '{color}' in required_mana.")
                return False  # Unknown mana type, deduction cannot proceed

            if temp_pool[color] >= required:
                temp_pool[color] -= required
                required_mana[color] = 0
            else:
                required -= temp_pool[color]
                temp_pool[color] = 0
                required_mana[color] = required

        if all(value == 0 for value in required_mana.values()):
            self.mana_available = temp_pool
            return True

        return False  # Not enough mana

    def play_turn(self):
        """
        Simulates a single turn of the game:
        1. Draw a card from the library if not empty.
        2. Play one land or basic land from the hand to the field.
        3. Play other cards from the hand based on CMC and available lands.
        4. Discard cards from hand if more than 7 are left.
        """
        self.turns += 1

        # Check termination conditions
        if self.turns >= 250:
            raise RuntimeError(f"Simulation aborted: Exceeded 250 turns (Current benchmark: {self.benchmark_score}).")
        if self.benchmark_score <= -250:
            raise RuntimeError("Simulation aborted: Benchmark score dropped below -250.")
        if self.benchmark_score >= 250:
            raise RuntimeError("Simulation aborted: Benchmark score exceeded +250.")

        print(f"\n=== Turn {self.turns} ===")
        print(f"Turn {self.turns}: Starting Benchmark Score: {self.benchmark_score}")
        print(f"Turn {self.turns}: Mana Pool: {self.mana_available}")
        print(f"Turn {self.turns}: Hand: {[card['name'] for card in self.hand]}")
        print(f"Turn {self.turns}: Field: {[card['name'] for card in self.field]}")
        print(f"Turn {self.turns}: Deck Size: {len(self.decklist)}")

        # 1. Draw a card from the library
        if self.decklist:
            drawn_card = self.decklist.pop()
            self.hand.append(drawn_card)
            print(f"Turn {self.turns}: Drew card: {drawn_card['name']}")
        else:
            print(f"Turn {self.turns}: No cards left in the deck to draw.")

        # 2. Play a land or basic land
        lands_in_hand = [card for card in self.hand if "land" in card.get("type", "").lower()]
        if lands_in_hand:
            land_to_play = lands_in_hand[0]  # Play the first land found
            self.field.append(land_to_play)
            self.hand.remove(land_to_play)

            # Add mana based on produced_mana
            for color in land_to_play.get("produced_mana", []):
                if color in self.mana_available:
                    self.mana_available[color] += 1
                else:
                    print(f"Turn {self.turns}: Warning: Unknown mana type '{color}' in {land_to_play['name']}")

            self.benchmark_score += 1  # Add 1 point for playing a land
            print(f"Turn {self.turns}: Played land: {land_to_play['name']}")
        else:
            self.benchmark_score -= 1  # Lose a point if no land is played
            print(f"Turn {self.turns}: No land played this turn.")

        print(f"Turn {self.turns}: Updated Mana Pool: {self.mana_available}")
        print(f"Turn {self.turns}: Updated Benchmark Score: {self.benchmark_score}")

        # 3. Play other cards based on CMC        
        cards_played = []

        # Always play cards with CMC = 0 that are not lands
        zero_cmc_non_lands = [card for card in self.hand if card.get("cmc", 0) == 0 and "land" not in card.get("type", "").lower()]
        for card in zero_cmc_non_lands:
            self.field.append(card)
            self.hand.remove(card)

            # Check if the card produces mana and add it to the mana pool
            if "produced_mana" in card:
                for color in card.get("produced_mana", []):
                    if color in self.mana_available:
                        self.mana_available[color] += 1
                    else:
                        print(f"Warning: Unknown mana type '{color}' produced by card '{card['name']}'")
            cards_played.append(card["name"])
            self.benchmark_score += 1  # Add 1 point for playing a card

        # Debugging: Display state after zero-CMC card plays
        print(f"Turn {self.turns}: Played zero-CMC cards: {cards_played}")
                
        # Find all combinations of cards with CMC > 0 that can be played within the available mana
        remaining_mana = self.mana_available.copy()
        best_combination = []
        max_mana_used = 0

        for r in range(1, len(self.hand) + 1):
            for combination in combinations(self.hand, r):
                total_cmc = sum(card.get("cmc", 0) for card in combination)
        
                can_play_combination = True                
                for card in combination:
                    mana_cost = card.get("mana_cost", "")
                    required_mana = {color: 0 for color in remaining_mana}

                    # Parse mana costs like {4}{U}{B}
                    for symbol in re.findall(r"\{(\d+|[WUBRGC])\}", mana_cost):
                        if symbol.isdigit():
                            required_mana["C"] += int(symbol)  # Treat generic mana as colorless initially
                        else:
                            required_mana[symbol.upper()] += 1

                    # Deduct specific mana first
                    for color in ["W", "U", "B", "R", "G"]:
                        if remaining_mana[color] >= required_mana[color]:
                            remaining_mana[color] -= required_mana[color]
                            required_mana[color] = 0
                        else:
                            required_mana[color] -= remaining_mana[color]
                            remaining_mana[color] = 0

                    # Deduct remaining generic mana (can be any type)
                    generic_mana_needed = required_mana["C"]
                    for color in ["W", "U", "B", "R", "G", "C"]:
                        if generic_mana_needed <= 0:
                            break
                        if remaining_mana[color] >= generic_mana_needed:
                            remaining_mana[color] -= generic_mana_needed
                            generic_mana_needed = 0
                        else:
                            generic_mana_needed -= remaining_mana[color]
                            remaining_mana[color] = 0

                    # If generic mana couldn't be satisfied, the combination is invalid
                    if generic_mana_needed > 0:
                        can_play_combination = False
                        break

                if can_play_combination and total_cmc > max_mana_used:
                    best_combination = combination
                    max_mana_used = total_cmc

        # After selecting the best combination, play the cards
        for card in best_combination:
            self.field.append(card)
            self.hand.remove(card)
            # Check if the card produces mana and add it to the mana pool
            if "produced_mana" in card:
                for color in card.get("produced_mana", []):
                    if color in self.mana_available:
                        self.mana_available[color] += 1
                    else:
                        print(f"Warning: Unknown mana type '{color}' produced by card '{card['name']}'")
            cards_played.append(card["name"])
            self.benchmark_score += 1  # Add 1 point for playing a card

        print(f"Turn {self.turns}: Played cards {cards_played}.")
        print(f"Turn {self.turns}: Mana pool after playing cards: {remaining_mana}")

        # 4. Discard cards if more than 7 are in hand
        if len(self.hand) > 7:
            excess_cards = len(self.hand) - 7
            discarded_cards = random.sample(self.hand, excess_cards)
            for card in discarded_cards:
                self.hand.remove(card)
            print(f"Turn {self.turns}: Discarded cards {[card['name'] for card in discarded_cards]}.")

    def display_state(self):
        """
        Debugging helper to display the current state.
        """
        print(f"Turn {self.turns}: Hand: {[card['name'] for card in self.hand]}")
        print(f"Turn {self.turns}: Deck size: {len(self.decklist)}")
        print(f"Turn {self.turns}: Field: {[card['name'] for card in self.field]}")
        print(f"Turn {self.turns}: Mana available: {self.mana_available}")
        print(f"Turn {self.turns}: Turns: {self.turns}")
        print(f"Turn {self.turns}: Benchmark score: {self.benchmark_score}")

    def simulate_game(self):
        """
        Simulates a full game by playing turns until the deck is empty
        and no more cards can be drawn.
        """
        self.start_new_round()
        while self.decklist or self.hand:
            self.play_turn()
        print(f"Turn {self.turns}: Game finished in {self.turns} turns.")
        print(f"Turn {self.turns}: Final Benchmark Score: {self.benchmark_score}")
        return {
            "benchmark_score": self.benchmark_score,
            "turns": self.turns
        }
