from game.deck import create_deck, shuffle_deck, deal_cards
from game.game_state import GameState
from game.rules import (
    get_suit,
    get_rank,
    is_valid_move,
    determine_trick_winner,
)


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


def get_highest_trump_played(game, trump):
    trump_cards = []

    for entry in game.cards_played:
        card = entry.split(": ")[1]

        if get_suit(card) == trump:
            trump_cards.append(card)

    if not trump_cards:
        return None

    return max(
        trump_cards,
        key=lambda card: {
            "Q": 0,
            "K": 1,
            "10": 2,
            "A": 3,
            "9": 4,
            "J": 5,
        }[get_rank(card)],
    )


def play_card(game, player, card):

    if player != game.current_turn:
        return False

    if player == game.player1:
        hand = game.player1_cards
    elif player == game.player2:
        hand = game.player2_cards
    else:
        return False

    if card not in hand:
        return False

    if not game.cards_played:
        leading_suit = get_suit(card)
        highest_trump_played = None
    else:
        first_card = game.cards_played[0].split(": ")[1]
        leading_suit = get_suit(first_card)

        highest_trump_played = get_highest_trump_played(
            game,
            game.trump,
        )

    if not is_valid_move(
        player_cards=hand,
        played_card=card,
        leading_suit=leading_suit,
        trump=game.trump,
        highest_trump_played=highest_trump_played,
    ):
        return False

    hand.remove(card)

    game.cards_played.append(
        f"{player}: {card}"
    )

    if player == game.player1:
        game.current_turn = game.player2
    else:
        game.current_turn = game.player1

    return True


def finish_trick(game):
    if len(game.cards_played) != 2:
        return None

    first_card = game.cards_played[0].split(": ")[1]
    second_card = game.cards_played[1].split(": ")[1]

    winner = determine_trick_winner(
        first_card,
        second_card,
        game.trump,
    )

    if winner == "first":
        return game.cards_played[0].split(": ")[0]

    return game.cards_played[1].split(": ")[0]


def apply_legal_move(game, player, card):
    """
    Apply a move only after the AI Referee has approved it.
    """

    if player != game.current_turn:
        return False

    if player == game.player1:
        hand = game.player1_cards
    elif player == game.player2:
        hand = game.player2_cards
    else:
        return False

    if card not in hand:
        return False

    hand.remove(card)

    game.cards_played.append(
        f"{player}: {card}"
    )

    if player == game.player1:
        game.current_turn = game.player2
    else:
        game.current_turn = game.player1

    return True