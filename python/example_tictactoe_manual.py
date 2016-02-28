import functools
from stratum_client import StratumClient, main

class TicTacToeClient(StratumClient):

    def __init__(self, settings):
        super(TicTacToeClient, self).__init__(settings)
        self._board = None
        self._winner = None

    def server_closed_connection(self):
        print("Game Over!")
        if self._winner:
            print("Player {} wins!".format(self._winner))
        else:
            print("Draw!")
    
    def message_received_from_server(self, message):
        if message["type"] == "state":
            self._board = message["board"]
            self._winner = message["winner"]
        elif message["type"] == "turn":
            print("\nYour turn!")
            board = list(map(lambda x: x or " ", functools.reduce(lambda x, y: x+y, self._board, [])))
            print("\n{} | {} | {}\n---------\n{} | {} | {}\n---------\n{} | {} | {}\n".format(*board))
            move = input("Your Move? (row, column) ")
            row, col = (int(x.strip()) for x in move.split(","))
            self.send_message_to_server({
                "type": "move",
                "row": row,
                "column": col
            })


if __name__ == "__main__":
    main(TicTacToeClient)
