import Env, sys, random
from Search import a_star_search

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
        obstacles = [x for y in self.state['obstacles'] for x in y] # convert to 1D list
        obstacles += self.state['snake']
        obstacles.append(self.state['food'][1])
        path = a_star_search(head, food, obstacles, self.grid_size)
        if path is None:
            return random.choice([Env.Vec2(0, -1), Env.Vec2(0, 1), Env.Vec2(-1, 0), Env.Vec2(1, 0)])
        return head.negate() + path[1]
    
    def play(self) -> None:
        self.engine.e.time.set_timer(self.engine.SCREEN_UPDATE, 105)
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
