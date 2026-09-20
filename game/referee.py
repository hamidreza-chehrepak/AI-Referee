from rules import get_move_violation


class AIReferee:

    def __init__(self, game_state):
        self.game = game_state

    def validate_move(self, player, card):

        if player == self.game.player1:
            hand = self.game.player1_cards

        elif player == self.game.player2:
            hand = self.game.player2_cards

        else:
            return {
                "decision": "ILLEGAL",
                "reason": "Unknown player.",
            }

        if player != self.game.current_turn:
            return {
                "decision": "ILLEGAL",
                "reason": "It is not this player's turn.",
            }

        if card not in hand:
            return {
                "decision": "ILLEGAL",
                "reason": "The card is not in the player's hand.",
            }

        if not self.game.cards_played:
            return {
                "decision": "LEGAL",
                "reason": "First card of the trick.",
            }

        first_card = self.game.cards_played[0].split(": ")[1]
        leading_suit = first_card[-1]

        violation = get_move_violation(
            player_cards=hand,
            played_card=card,
            leading_suit=leading_suit,
            trump=self.game.trump,
        )

        if violation is None:
            return {
                "decision": "LEGAL",
                "reason": "Move follows the game rules.",
            }

        return {
            "decision": "ILLEGAL",
            "reason": violation,
        }

    def judge_move(self, player, card):

        result = self.validate_move(
            player,
            card,
        )

        print("\n=== AI REFEREE DECISION ===")
        print(f"Player: {player}")
        print("Action: PLAY_CARD")
        print(f"Card: {card}")
        print(f"Decision: {result['decision']}")
        print(f"Reason: {result['reason']}")

        return result