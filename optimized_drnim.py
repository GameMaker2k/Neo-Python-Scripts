
def play_nim(player_first=True, total_coins=12):
    """
    Play a round of Nim.

    :param player_first: Boolean, True if the player goes first, False otherwise.
    :param total_coins: Integer, total number of coins in the game.
    :return: Boolean, True if player wins, False if Dr. Nim wins.
    """
    def nim_move(coins):
        """
        Calculate Dr. Nim's move.

        :param coins: Integer, current number of coins.
        :return: Integer, number of coins Dr. Nim will take.
        """
        return 1 if coins % 4 == 1 else 4 - (coins % 4)

    def player_move(coins, player_choice):
        """
        Process player's move.

        :param coins: Integer, current number of coins.
        :param player_choice: Integer, number of coins the player chooses to take.
        :return: Integer, remaining number of coins.
        """
        return coins - player_choice

    coins = total_coins
    while coins > 0:
        if player_first:
            player_choice = 3  # Assuming the player always takes 3 coins
            coins = player_move(coins, player_choice)
            player_first = False
        else:
            nim_choice = nim_move(coins)
            coins = player_move(coins, nim_choice)
            player_first = True

        if coins <= 0:
            return not player_first


# Running multiple rounds and tracking wins and losses
player_wins = 0
dr_nim_wins = 0
for round in range(1, 13):
    if play_nim(player_first=round % 2 == 0):
        player_wins += 1
    else:
        dr_nim_wins += 1

print("Player Wins:", player_wins)
print("Dr. Nim Wins:", dr_nim_wins)
