import Env, sys
from collections import deque
from Search import a_star_search

MAX_MEMORY: int = 100_000
BATCH_SIZE: int = 1000

class Agent:
    def __init__(self, engine: object) -> None:
        self.engine = engine
        self.num_games = 0
        self.grid_size = self.engine.cell_number
        self.state = self.get_state()

    def get_state(self) -> None:
        raise NotImplementedError("get_state method must be implemented!")

    def choose_action(self) -> 'Env.Vec2':
        raise NotImplementedError("choose_action method must be implemented!")

    def play(self) -> None:
        raise NotImplementedError("play method must be implemented!")

class SearchAgent(Agent):
    def __init__(self, engine: object) -> None:
        super().__init__(engine)

    def get_state(self) -> None:
        return self.engine.env_state

    def choose_action(self) -> Env.Vec2:
        head = self.state['snake'][0]
        food = self.state['food'][0]
        path = a_star_search(head, food, self.state['obstacles'], self.grid_size)
        return head.negate() + path[1]
    
    def play(self) -> None:
        self.engine.e.time.set_timer(self.engine.SCREEN_UPDATE, 20)
        self.engine.running = True
        while self.engine.running:
            action = self.choose_action()
            self.engine.event_manager.handle_events(action)
                
            if self.engine.death:
                self.engine.reset_game()
            
            self.engine.event_manager.handle_keys(action)
            self.engine.renderer.update_high_score()
            self.engine.renderer.draw()
            self.engine.e.display.flip() # use flip instead of update for a complete frame update
            self.engine.clock.tick(self.engine.fps) # set framerate
        
        self.engine.e.quit()
        sys.exit()

# class RLAgent(Agent):
#     def __init__(self) -> None:
#         super().__init__()
#         self.ε = 0
#         self.γ = 0
#         self.lr = 0.001
#         self.memory = deque(maxlen=MAX_MEMORY)
#         # self.model = model

#     def get_state(self) -> None:
#         # get the current state of the environment...
#         # i.e snake(s) position(s), food positions(s) and obstacles
#         pass

#     def choose_action(self) -> None:
#         # use trained model to get best action given a state
#         pass

#     def play(self) -> None:
#         # play game based on guidance from model
#         pass

#     def train(self) -> None:
#         # train model based on env state and reward
#         pass

# model = ... # Load trained model
# env = ... # set up environment
# agent = # SearchAgent()
# agent.play()