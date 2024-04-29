import sys
from Env import Engine
from Env_controller import GameController
from Agent import SearchAgent, RLAgent

def snake_game():
    game_engine = Engine()
    
    # Determine the mode of play based on command line arguments
    mode = sys.argv[1] if len(sys.argv) > 1 else 'rl'
    
    if mode.lower() == 'rl':
        agent = RLAgent(game_engine)
        agent.train()
    elif mode.lower() == 'ai':
        # Run the game with an AI agent
        agent = SearchAgent(game_engine)
        agent.play()
    elif mode.lower() == 'human':
        # Run the game with human controls
        game_controller = GameController(game_engine)
        game_controller.run_game()
    else:
        print("Invalid mode. Please choose 'rl', 'ai' or 'human'.")

if __name__ == "__main__":
    snake_game()