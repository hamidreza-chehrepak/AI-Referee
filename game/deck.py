SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["9", "10", "J", "Q", "K", "A"]


def create_deck():
    return [f"{rank}{suit}" for suit in SUITS for rank in RANKS]



import random


def shuffle_deck(deck):
    random.shuffle(deck)
    return deck


def deal_cards(deck):
    player1 = deck[:12]
    player2 = deck[12:]
    return player1, player2



def choose_trump(suit):
    return suit