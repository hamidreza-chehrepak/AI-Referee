def get_suit(card: str) -> str:
    return card[-1]


def has_suit(cards: list[str], suit: str) -> bool:
    return any(get_suit(card) == suit for card in cards)


def is_valid_move(
    player_cards: list[str],
    played_card: str,
    leading_suit: str,
) -> bool:
    """
    بررسی قانون Follow Suit:

    اگر بازیکن خال شروع‌شده را داشته باشد،
    باید کارتی از همان خال بازی کند.

    اگر آن خال را نداشته باشد،
    فعلاً حرکت مجاز است.
    """

    if played_card not in player_cards:
        return False

    if has_suit(player_cards, leading_suit):
        return get_suit(played_card) == leading_suit

    return True