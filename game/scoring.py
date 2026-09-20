from collections import Counter


TRUMP_CARD_POINTS = {
    "J": 20,
    "9": 14,
    "A": 11,
    "10": 10,
    "K": 4,
    "Q": 3,
}

NON_TRUMP_CARD_POINTS = {
    "A": 11,
    "10": 10,
    "K": 4,
    "Q": 3,
    "J": 2,
    "9": 0,
}


def get_suit(card: str) -> str:
    return card[-1]


def get_rank(card: str) -> str:
    return card[:-1]


def card_points(card: str, trump: str) -> int:
    """
    Return the point value of a card.
    """

    rank = get_rank(card)
    suit = get_suit(card)

    if suit == trump:
        return TRUMP_CARD_POINTS[rank]

    return NON_TRUMP_CARD_POINTS[rank]


def trick_points(
    cards: list[str],
    trump: str,
    is_last_trick: bool = False,
) -> int:
    """
    Calculate points collected from a trick.

    The winner of the last trick receives an additional 10 points.
    """

    total = sum(
        card_points(card, trump)
        for card in cards
    )

    if is_last_trick:
        total += 10

    return total


def hand_card_points(
    cards: list[str],
    trump: str,
) -> int:
    """
    Calculate the total card points collected by a player.
    """

    return sum(
        card_points(card, trump)
        for card in cards
    )


def four_of_a_kind_points(
    cards: list[str],
    trump: str,
) -> int:
    """
    Calculate Four of a Kind points.

    Trump:
        J = 200
        9 = 140
        A = 110
        Q/K/10 = 100

    Non-trump:
        A = 190
        10/K/Q/J = 100
        9 = 0
    """

    ranks = Counter(get_rank(card) for card in cards)

    total = 0

    for rank, count in ranks.items():

        if count != 4:
            continue

        four_cards = [
            card
            for card in cards
            if get_rank(card) == rank
        ]

        trump_count = sum(
            get_suit(card) == trump
            for card in four_cards
        )

        if trump_count == 1:

            if rank == "J":
                total += 200
            elif rank == "9":
                total += 140
            elif rank == "A":
                total += 110
            else:
                total += 100

        else:

            if rank == "A":
                total += 190
            elif rank == "9":
                total += 0
            else:
                total += 100

    return total


def sequence_length(cards: list[str]) -> int:
    """
    Return the longest consecutive sequence
    within cards of the same suit.

    Card sequence for Simple Belote:

    9, 10, J, Q, K, A
    """

    sequence_order = {
        "9": 0,
        "10": 1,
        "J": 2,
        "Q": 3,
        "K": 4,
        "A": 5,
    }

    by_suit = {}

    for card in cards:
        suit = get_suit(card)
        rank = get_rank(card)

        by_suit.setdefault(suit, set()).add(
            sequence_order[rank]
        )

    longest = 0

    for ranks in by_suit.values():

        ordered = sorted(ranks)

        current = 1

        for i in range(1, len(ordered)):

            if ordered[i] == ordered[i - 1] + 1:
                current += 1
            else:
                current = 1

            longest = max(longest, current)

    return longest


def combination_points(cards: list[str], trump: str) -> int:
    """
    Calculate combination points.

    Four of a Kind:
        J = 200
        9 = 140
        A = 110
        Q/K/10 = 100

    Hundred:
        5-card sequence = 100

    Fifty:
        4-card sequence = 50

    Tierce:
        3-card sequence = 20

    Belote:
        K + Q of trump = 20
    """

    total = 0

    # Four of a Kind
    total += four_of_a_kind_points(
        cards,
        trump,
    )

    # Sequence
    longest = sequence_length(cards)

    if longest >= 5:
        total += 100
    elif longest == 4:
        total += 50
    elif longest == 3:
        total += 20

    # Belote
    trump_ranks = {
        get_rank(card)
        for card in cards
        if get_suit(card) == trump
    }

    if {"K", "Q"}.issubset(trump_ranks):
        total += 20

    return total


def total_hand_score(
    cards: list[str],
    trump: str,
    is_last_trick_winner: bool = False,
) -> int:
    """
    Calculate the total score for a player's hand.

    Includes:
        - card points
        - combinations
        - optional last-trick 10 points
    """

    total = hand_card_points(
        cards,
        trump,
    )

    total += combination_points(
        cards,
        trump,
    )

    if is_last_trick_winner:
        total += 10

    return total


def calculate_round_scores(
    player1_cards: list[str],
    player2_cards: list[str],
    trump: str,
    taker: str,
    player1_last_trick: bool,
    player2_last_trick: bool,
) -> tuple[int, int]:
    """
    Calculate the final scores of a round.

    The player who chose trump must score more points
    than the opponent.

    If the taker does not score more, the round points
    are transferred to the opponent.

    If the taker collects no points, this is Kaput.
    In the two-player version, the opponent receives
    21 additional points.
    """

    player1_score = total_hand_score(
        player1_cards,
        trump,
        player1_last_trick,
    )

    player2_score = total_hand_score(
        player2_cards,
        trump,
        player2_last_trick,
    )

    if taker == "Player 1":

        if player1_score == 0:
            return 0, player2_score + 21

        if player1_score <= player2_score:
            return 0, player1_score + player2_score

    elif taker == "Player 2":

        if player2_score == 0:
            return player1_score + 21, 0

        if player2_score <= player1_score:
            return player1_score + player2_score, 0

    return player1_score, player2_score


if __name__ == "__main__":

    trump = "♠"

    test_cards = [
        "J♠",
        "9♠",
        "A♠",
        "10♠",
        "K♠",
        "Q♠",
    ]

    print("=== Scoring Engine Test ===")
    print("Trump:", trump)

    for card in test_cards:
        print(
            card,
            "->",
            card_points(card, trump),
            "points",
        )

    print(
        "Total card points:",
        hand_card_points(test_cards, trump),
    )

    print(
        "Combination points:",
        combination_points(test_cards, trump),
    )