CARD_VALUES_NORMAL = {
    "9": 0,
    "J": 2,
    "Q": 3,
    "K": 4,
    "10": 10,
    "A": 11,
}

CARD_VALUES_TRUMP = {
    "9": 14,
    "J": 20,
    "Q": 3,
    "K": 4,
    "10": 10,
    "A": 11,
}

CARD_ORDER_NORMAL = {
    "9": 0,
    "J": 1,
    "Q": 2,
    "K": 3,
    "10": 4,
    "A": 5,
}

CARD_ORDER_TRUMP = {
    "Q": 0,
    "K": 1,
    "10": 2,
    "A": 3,
    "9": 4,
    "J": 5,
}


def get_suit(card: str) -> str:
    return card[-1]


def get_rank(card: str) -> str:
    return card[:-1]


def has_suit(cards: list[str], suit: str) -> bool:
    return any(get_suit(card) == suit for card in cards)


def get_move_violation(
    player_cards: list[str],
    played_card: str,
    leading_suit: str,
    trump: str | None = None,
    highest_trump_played: str | None = None,
) -> str | None:

    if played_card not in player_cards:
        return "The card is not in the player's hand."

    played_suit = get_suit(played_card)

    if has_suit(player_cards, leading_suit):

        if played_suit != leading_suit:
            return (
                f"Player has the leading suit {leading_suit} "
                f"and must follow suit."
            )

        return None

    if trump is None:
        return None

    if has_suit(player_cards, trump):

        if played_suit != trump:
            return (
                f"Player has the trump suit {trump} "
                f"and must play trump."
            )

        if highest_trump_played is not None:

            played_rank = get_rank(played_card)
            highest_rank = get_rank(highest_trump_played)

            if (
                CARD_ORDER_TRUMP[played_rank]
                <= CARD_ORDER_TRUMP[highest_rank]
            ):
                return (
                    f"Player must overtrump {highest_trump_played} "
                    f"when a stronger trump is available."
                )

        return None

    return None


def is_valid_move(
    player_cards: list[str],
    played_card: str,
    leading_suit: str,
    trump: str | None = None,
    highest_trump_played: str | None = None,
) -> bool:

    return (
        get_move_violation(
            player_cards,
            played_card,
            leading_suit,
            trump,
            highest_trump_played,
        )
        is None
    )


def card_value(
    card: str,
    trump: str | None = None,
) -> int:

    rank = get_rank(card)

    if trump is not None and get_suit(card) == trump:
        return CARD_VALUES_TRUMP[rank]

    return CARD_VALUES_NORMAL[rank]


def card_strength(
    card: str,
    trump: str | None = None,
) -> int:

    rank = get_rank(card)
    suit = get_suit(card)

    if trump is not None and suit == trump:
        return 100 + CARD_ORDER_TRUMP[rank]

    return CARD_ORDER_NORMAL[rank]


def determine_trick_winner(
    first_card: str,
    second_card: str,
    trump: str | None = None,
) -> str:

    leading_suit = get_suit(first_card)

    first_is_trump = (
        trump is not None
        and get_suit(first_card) == trump
    )

    second_is_trump = (
        trump is not None
        and get_suit(second_card) == trump
    )

    if second_is_trump and not first_is_trump:
        return "second"

    if first_is_trump and not second_is_trump:
        return "first"

    if get_suit(second_card) != leading_suit:
        return "first"

    if card_strength(second_card, trump) > card_strength(
        first_card,
        trump,
    ):
        return "second"

    return "first"