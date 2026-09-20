from deck import create_deck, shuffle_deck, deal_cards
from game_state import GameState
from rules import (
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
    """
    از کارت‌های Trick فعلی، قوی‌ترین حکم بازی‌شده را پیدا می‌کند.
    """

    trump_cards = []

    for entry in game.cards_played:
        card = entry.split(": ")[1]

        if get_suit(card) == trump:
            trump_cards.append(card)

    if not trump_cards:
        return None

    return max(
        trump_cards,
        key=lambda card: (
            {
                "Q": 0,
                "K": 1,
                "10": 2,
                "A": 3,
                "9": 4,
                "J": 5,
            }[get_rank(card)]
        ),
    )


def play_card(game, player, card):

    # بررسی نوبت
    if player != game.current_turn:
        return False

    # انتخاب دست بازیکن
    if player == game.player1:
        hand = game.player1_cards
    elif player == game.player2:
        hand = game.player2_cards
    else:
        return False

    # کارت باید در دست بازیکن باشد
    if card not in hand:
        return False

    # کارت اول Trick
    if not game.cards_played:
        leading_suit = get_suit(card)
        highest_trump_played = None

    # کارت دوم Trick
    else:
        first_card = game.cards_played[0].split(": ")[1]
        leading_suit = get_suit(first_card)

        highest_trump_played = get_highest_trump_played(
            game,
            game.trump,
        )

    # بررسی قوانین
    if not is_valid_move(
        player_cards=hand,
        played_card=card,
        leading_suit=leading_suit,
        trump=game.trump,
        highest_trump_played=highest_trump_played,
    ):
        return False

    # حذف کارت از دست
    hand.remove(card)

    # ثبت حرکت
    game.cards_played.append(
        f"{player}: {card}"
    )

    # تغییر نوبت
    if player == game.player1:
        game.current_turn = game.player2
    else:
        game.current_turn = game.player1

    return True


def finish_trick(game):
    """
    وقتی دو بازیکن کارت بازی کردند،
    برنده Trick را مشخص می‌کند.
    """

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


if __name__ == "__main__":

    game = create_game()

    # برای تست فعلاً حکم را دستی مشخص می‌کنیم
    game.trump = "♠"

    print("=== AI Referee Game State ===")
    print("Trump:", game.trump)
    print("Player 1:", game.player1_cards)
    print("Player 2:", game.player2_cards)

    # حرکت اول
    first_card = game.player1_cards[0]

    print("\nPlayer 1 plays:", first_card)

    result = play_card(
        game,
        "Player 1",
        first_card,
    )

    print("Move accepted:", result)
    print("Played cards:", game.cards_played)
    print("Next turn:", game.current_turn)

    # حرکت دوم: اولین کارت قانونی
    second_card = None

    for card in game.player2_cards:

        highest_trump = get_highest_trump_played(
            game,
            game.trump,
        )

        first_card_played = game.cards_played[0].split(": ")[1]

        if is_valid_move(
            game.player2_cards,
            card,
            get_suit(first_card_played),
            game.trump,
            highest_trump,
        ):
            second_card = card
            break

    if second_card is not None:

        print("\nPlayer 2 plays:", second_card)

        result = play_card(
            game,
            "Player 2",
            second_card,
        )

        print("Move accepted:", result)
        print("Played cards:", game.cards_played)

        winner = finish_trick(game)

        print("\n=== Trick Result ===")
        print("Winner:", winner)

    else:
        print("\nPlayer 2 has no legal move.")