from deck import create_deck, shuffle_deck, deal_cards
from game_state import GameState
from rules import is_valid_move


def create_game():
    deck = create_deck()
    shuffle_deck(deck)

    player1_cards, player2_cards = deal_cards(deck)

    return GameState(
        player1="Player 1",
        player2="Player 2",
        player1_cards=player1_cards,
        player2_cards=player2_cards,
        current_turn="Player 1",
    )


def play_card(game, player, card, leading_suit=None):
    if player == game.player1:
        hand = game.player1_cards
    elif player == game.player2:
        hand = game.player2_cards
    else:
        return False

    if card not in hand:
        return False

    if leading_suit is not None:
        if not is_valid_move(hand, card, leading_suit):
            return False

    hand.remove(card)
    game.cards_played.append(f"{player}: {card}")

    if player == game.player1:
        game.current_turn = game.player2
    else:
        game.current_turn = game.player1

    return True


if __name__ == "__main__":
    game = create_game()

    print("=== AI Referee Game State ===")
    print("Player 1:", game.player1_cards)
    print("Player 2:", game.player2_cards)

    first_card = game.player1_cards[0]
    first_suit = first_card[-1]

    print("Player 1 plays:", first_card)

    result = play_card(
        game,
        "Player 1",
        first_card,
        first_suit
    )

    print("Move accepted:", result)
    print("Played cards:", game.cards_played)
    print("Next turn:", game.current_turn)