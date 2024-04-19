from Env import Engine
from Env_contoller import GameController

if __name__ == "__main__":
    game_engine = Engine()
    game_controller = GameController(game_engine)
    game_controller.run_game()