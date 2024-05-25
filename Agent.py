import Env, sys, random, torch, numpy as np # type: ignore
from Search import a_star_search
from collections import deque
from DeepQN import DQN, Trainer
import logging
from datetime import datetime

MAX_MEMORY = 100_000
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
    def __init__(self, engine: object, lr, ε, ε_min, ε_decay, γ, nn_hidden) -> None:
        super().__init__(engine)
        self.ε = ε
        self.ε_min = ε_min
        self.ε_decay = ε_decay
        self.γ = γ
        self.lr = lr
        self.nn_hidden = nn_hidden
        self.hidden_layers = [pow(2, 8)]
        self.hidden_layers = self.nn_hidden * self.hidden_layers
        print(self.engine.rl_state)
         
        self.state_size = len(self.engine.rl_state)
        print(f"State size = {self.state_size}")
        self.action_size = 3 
        self.replay_buffer = deque(maxlen=MAX_MEMORY)
        self.model = DQN(self.state_size, self.hidden_layers, self.action_size)
        self.trainer = Trainer(self.model, lr=self.lr, γ = self.γ)
        self.ACTION = [0, 0, 0]

    def get_state(self) -> list:
        return self.engine.rl_state
    
    def update_epsilon(self) -> None:
        self.ε = max(self.ε_min, self.ε * self.ε_decay)
    
    def get_direction(self, move: list) -> 'Env.Vec2':
        action = Env.Vec2(0, 0)
        if move == [1, 0, 0]: # move straight
            action = self.engine.snake.head - self.engine.snake.body[1]
        elif move == [0, 1, 0]: # move right
            dir = self.engine.snake.head - self.engine.snake.body[1]
            action = dir.swap() if dir.x != 0 else -dir.swap()
        elif move == [0, 0, 1]: # move left
            dir = self.engine.snake.head - self.engine.snake.body[1]
            action = -dir.swap() if dir.x != 0 else dir.swap()
        return action
    
    def choose_action(self, state: list) -> Env.Vec2:
        # epsilon-greedy
        move = [0, 0, 0]
        if np.random.rand() <= self.ε:
            move_idx = random.randint(0, 2)
            move[move_idx] = 1
            # print(f"Move = {move}")
        else:
            stateCopy = state.copy()
            stateCopy = torch.tensor(stateCopy, dtype=torch.float32)
            prediction = self.model(stateCopy)
            print(f"Prediction = {prediction}")
            move_idx = torch.argmax(prediction).item()
            move[move_idx] = 1
        self.ACTION = move
        dir = self.get_direction(move)
        return dir

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

    def setup_logging(self):
        # Create a custom logger
        self.logger = logging.getLogger(__name__)
        
        # Set the log level
        self.logger.setLevel(logging.INFO)
        
        # Create handlers (console and file handlers)
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(f'rl_agent_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)
        
        # Add handlers to the logger
        self.logger.addHandler(c_handler)
        self.logger.addHandler(f_handler)

    def log_performance(self, score, reward, epsilon, state, action, dir):
        # Log performance metrics
        # self.logger.info(f'Game: {self.num_games}, Score: {score}, Reward: {reward}, Epsilon: {epsilon} State: {state} Action: {action} SnakeDirection: {dir}')
        self.logger.info(f'Game: {self.num_games}, Score: {score}, Reward: {reward}, Epsilon: {epsilon}')

    def play(self) -> None:
        return super().play()

    def train(self) -> None:
        plot_scores = []
        plot_mean_scores = []
        total_score = 0
        self.engine.e.time.set_timer(self.engine.SCREEN_UPDATE, 60)
        self.engine.running = True
        reward = 0
        
        while self.engine.running:
            state = self.get_state()
            dir = self.engine.snake.body[0] - self.engine.snake.body[1]
            action = self.choose_action(state) 
            self.engine.event_manager.handle_keys(action) # play action/step function
            reward += self.engine.reward
            self.engine.event_manager.handle_events() # refresh game_state/display or quit
            self.engine.renderer.update_high_score()
            next_state = self.get_state()
            self.train_short_term_memory(state, self.ACTION, self.engine.reward,
                                        next_state, self.engine.death)    

            if self.engine.death:
                self.log_performance(self.engine.snake.score, reward, self.ε, state, self.ACTION, dir)
                # train long term memory and plot results
                self.train_long_term_memory()
                self.update_epsilon()
                self.num_games += 1

                if self.engine.snake.score >= self.engine.renderer.high_score:
                    self.model.save()
                # print(f"Game {self.num_games}, Score {self.engine.snake.score},HighScore {self.engine.renderer.high_score}, Reward {reward},Epsilon {self.ε}")

                plot_scores.append(self.engine.snake.score)
                total_score += self.engine.snake.score
                self.engine.reset_game()
                reward = 0
                mean_score = total_score / self.num_games
                plot_mean_scores.append(mean_score)
                plotter = Env.Plotter(plot_scores, plot_mean_scores)
                plotter.plot()

            self.engine.renderer.draw()
            self.engine.e.display.flip() # use flip instead of update for a complete frame update
            self.engine.clock.tick(self.engine.fps) # set framerate
        
        self.engine.e.quit()
        sys.exit()