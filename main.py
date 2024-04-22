import sys
from Env import Engine
from Env_contoller import GameController
from Agent import SearchAgent

if __name__ == "__main__":
    game_engine = Engine()
    
    if len(sys.argv) == 1 or sys.argv[1] == 'ai':
        agent = SearchAgent(game_engine)
        agent.play()
    elif sys.argv[1] == 'human':
        game_controller = GameController(game_engine)
        game_controller.run_game()