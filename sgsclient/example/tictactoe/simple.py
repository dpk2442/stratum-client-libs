from sgsclient import StratumGSClientInstance, main

class TicTacToeClient(StratumGSClientInstance):

    def __init__(self, *args):
        super(TicTacToeClient, self).__init__(*args)
        self._board = None
        self._winner = None

    def server_closed_connection(self):
        print("Game Over!")
        if self._winner:
            print("Player {} wins!".format(self._winner))
        else:
            print("Draw!")

    def _find_empty_cell(self):
        for r, row in enumerate(self._board):
            for c, cell in enumerate(row):
                if cell is None:
                    return r, c

    def message_received_from_server(self, message):
        if message["type"] == "state":
            self._board = message["board"]
            self._winner = message["winner"]
        elif message["type"] == "turn":
            row, col = self._find_empty_cell()
            self.send_message_to_server({
                "type": "move",
                "row": row,
                "column": col
            })


if __name__ == "__main__":
    main(TicTacToeClient)
