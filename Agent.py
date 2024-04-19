class Agent:
    def __init__(self, model, environment) -> None:
        self.model = model
        self.env = environment

    def get_state(self) -> None:
        # get the current state of the environment...
        # i.e snake position(s), food positions(s) and obstacles
        pass

    def choose_action(self) -> None:
        # use trained model to get best action given a state
        pass

    def play(self) -> None:
        # play game based on training or...
        # train model based on env state and reward
        pass

# model = ... # Load trained model
# env = ... # set up environment
# agent = # Agent(model, env)
# agent.play()