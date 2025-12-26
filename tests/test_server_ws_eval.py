import asyncio
import sys
import pathlib

# Thêm thư mục cha vào sys.path để import module server_ws
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import server_ws

class Dummy:
    def __init__(self, move, addr):
        self.move = move
        self.ws = type('A', (), {'remote_address': addr})
        self.opponent = None

    async def send(self, data):
        print(f"SEND to {self.ws.remote_address}: {data}")

    def reset_move(self):
        self.move = None

async def run_test():
    p1 = Dummy('ROCK', '127.0.0.1:5000')
    p2 = Dummy('SCISSORS', '127.0.0.1:5001')
    p1.opponent = p2
    p2.opponent = p1

    print('Before evaluate_game: p1.move=', p1.move, 'p2.move=', p2.move)
    await server_ws.evaluate_game(p1)

if __name__ == '__main__':
    asyncio.run(run_test())
