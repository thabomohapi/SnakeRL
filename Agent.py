import Env, sys, random, torch, numpy as np # type: ignore
from Search import a_star_search
from collections import deque
from DeepQN import DQN, Trainer

MAX_MEMORY = 100000
BATCH_SIZE = 1000

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
        obstacles += self.state['snake'][1:-1]
        path = a_star_search(head, food, obstacles, self.grid_size, self.state['snake'])
        if path is None or len(path) < 2:
            return random.choice([Env.Vec2(0, -1), Env.Vec2(0, 1), Env.Vec2(-1, 0), Env.Vec2(1, 0)])
        return head.negate() + path[1]
    
    def play(self) -> None:
        self.engine.e.time.set_timer(self.engine.SCREEN_UPDATE, 80)
        self.engine.running = True
        while self.engine.running:
            action = self.choose_action()
            self.engine.event_manager.handle_keys(action)
            self.engine.event_manager.handle_events()
            self.engine.renderer.update_high_score()

            if self.engine.death:
                self.engine.reset_game()
            
            self.engine.renderer.draw()
            self.engine.e.display.flip() # use flip instead of update for a complete frame update
            self.engine.clock.tick(self.engine.fps) # set framerate
        
        self.engine.e.quit()
        sys.exit()

class RLAgent(Agent):
    def __init__(self, engine: object, lr = 0.01, ε = 1.0, γ = 0.75) -> None:
        super().__init__(engine)
        self.ε = ε
        self.ε_min = 0.01
        self.ε_decay = 0.995
        self.γ = γ
        self.lr = lr
        # print(self.engine.rl_state)
        self.state = self.get_state()
        self.state_size = len(self.engine.rl_state)
        # print(f"State size = {self.state_size}")
        self.action_size = 3 
        self.replay_buffer = deque(maxlen=MAX_MEMORY)
        self.model = DQN(self.state_size, pow(2, 8), pow(2, 8), pow(2, 8), self.action_size)
        self.trainer = Trainer(self.model, lr=self.lr, γ = self.γ)
        self.ACTION = [1, 0, 0]

    def get_state(self) -> list:
        return self.engine.rl_state
    
    def update_epsilon(self) -> None:
        self.ε = max(self.ε_min, self.ε * self.ε_decay)
    
    def convert_move_to_action(self, move: list) -> 'Env.Vec2':
        action = Env.Vec2(0, 0)
        if move == [1, 0, 0]: # move straight
            action = self.engine.snake.head + self.engine.snake.body[1].negate()
        elif move == [0, 1, 0]: # move right
            dir = self.engine.snake.head + self.engine.snake.body[1].negate()
            action = dir.swap() if dir.x != 0 else dir.swap().negate()
        else: # move left
            dir = self.engine.snake.head + self.engine.snake.body[1].negate()
            action = dir.swap().negate() if dir.x != 0 else dir.swap()
        return action
    
    def choose_action(self) -> Env.Vec2:
        # epsilon-greedy
        # self.ε = 80 - self.num_games
        move = [0, 0, 0]
        if np.random.rand() <= self.ε:
            move_idx = random.randint(0, 2)
            move[move_idx] = 1
        # if random.randint(0, 200) < self.ε:
        #     move_idx = random.randint(0, 2)
        #     move[move_idx] = 1
        else:
            state = self.state.copy()
            state = torch.tensor(state, dtype=torch.float32)
            prediction = self.model(state)[0]
            move_idx = torch.argmax(prediction).item()
            move[move_idx] = 1
        self.ACTION = move
        return self.convert_move_to_action(move)

    def remember(self, state, action, reward, next_state, death) -> None:
        self.replay_buffer.append((state, action, reward, next_state, death))

    def train_short_term_memory(self, state, action, reward, next_state, death) -> None:
        self.trainer.train(state, action, reward, next_state, death)
        self.remember(state, action, reward, next_state, death)

    def train_long_term_memory(self) -> None:
        if len(self.replay_buffer) > BATCH_SIZE:
            sub_sample = random.sample(self.replay_buffer, BATCH_SIZE)
        else:
            sub_sample = self.replay_buffer
        states, actions, rewards, next_states, deaths = zip(*sub_sample)
        self.trainer.train(states, actions, rewards, next_states, deaths)

    def play(self) -> None:
        return super().play()

    def train(self) -> None:
        plot_scores = []
        plot_mean_scores = []
        total_score = 0
        self.engine.e.time.set_timer(self.engine.SCREEN_UPDATE, 80)
        self.engine.running = True
        
        while self.engine.running:
            state = self.state
            action = self.choose_action()
            self.engine.event_manager.handle_keys(action) # play action/step function

            self.engine.event_manager.handle_events() # refresh game_state/display
            self.engine.renderer.update_high_score()

            self.train_short_term_memory(state, self.ACTION, self.engine.reward,
                                        self.get_state(), self.engine.death)    
            
            if self.engine.death:
                # train long term memory and plot results
                self.train_long_term_memory()
                self.update_epsilon()
                self.num_games += 1

                if self.engine.snake.score >= self.engine.renderer.high_score:
                    self.model.save()
                print(f"Game {self.num_games}, Score {self.engine.snake.score}, HighScore {self.engine.renderer.high_score}, Reward {self.engine.reward}")

                plot_scores.append(self.engine.snake.score)
                total_score += self.engine.snake.score
                self.engine.reset_game()
                mean_score = total_score / self.num_games
                plot_mean_scores.append(mean_score)
                plotter = Env.Plotter(plot_scores, plot_mean_scores)
                plotter.plot()

            self.engine.renderer.draw()
            self.engine.e.display.flip() # use flip instead of update for a complete frame update
            self.engine.clock.tick(self.engine.fps) # set framerate
        
        self.engine.e.quit()
        sys.exit()