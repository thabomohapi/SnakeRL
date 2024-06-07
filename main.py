from Env import Environment
from Env_controller import GameController
from Agent import SearchAgent, RLAgent

import tkinter as tk
from tkinter import Scale, Radiobutton, Button, Frame

def snake_game(mode, learning_rate, discount_factor, hidden_layers, epsilon, epsilon_decay, epsilon_min, rl_mode = None):
    env = Environment()
    if mode.lower() == 'rl':
        agent = RLAgent(env, lr=learning_rate, ε=epsilon, ε_min=epsilon_min, ε_decay=epsilon_decay, γ=discount_factor, nn_hidden=hidden_layers)
        if rl_mode == 'play':
            agent.play()
        else:
            agent.train()
    elif mode.lower() == 'search':
        # Run the game with an AI agent
        agent = SearchAgent(env)
        agent.play()
    elif mode.lower() == 'human':
        # Run the game with human controls
        game_controller = GameController(env)
        game_controller.run_game()
    else:
        print("Invalid mode. Please choose 'rl', 'search' or 'human'.")

def start_gui():
    def run_game():
        # Retrieve user-selected values from the sliders and radio buttons
        mode = mode_var.get()
        learning_rate = learning_rate_slider.get()
        discount_factor = discount_factor_slider.get()
        hidden_layers = hidden_layers_slider.get()
        epsilon = epsilon_slider.get()
        epsilon_decay = epsilon_decay_slider.get()
        epsilon_min = epsilon_min_slider.get()
        rl_mode = rl_mode_var.get()

        # Call the snake_game function with the selected parameters
        snake_game(mode, learning_rate, discount_factor, hidden_layers, epsilon, epsilon_decay, epsilon_min, rl_mode)
    
    def close_window(event=None):
        root.destroy()

    def toggle_sliders(*args):
        mode = mode_var.get()
        if mode == 'rl':
            # Show the sliders for RL mode
            for slider in sliders:
                slider.grid(sticky='nsew', padx=10, pady=5)
            train_radio.grid(sticky='nsew', padx=10, pady=5)
            play_radio.grid(sticky='nsew', padx=10, pady=5)
        else:
            # Hide the sliders for other modes
            for slider in sliders:
                slider.grid_remove()
            train_radio.grid_remove()
            play_radio.grid_remove()

    root = tk.Tk()
    root.title("Snake Game Parameters")

    # Bind the Escape key to the close_window function
    root.bind('<Escape>', close_window)

    # Configure the grid layout to auto-resize
    root.grid_columnconfigure(0, weight=1)
    for i in range(12):  # Adjust the range based on the number of rows needed
        root.grid_rowconfigure(i, weight=1)

    # Create a variable to store the selected mode
    mode_var = tk.StringVar(value="rl")
    mode_var.trace('w', toggle_sliders)  # Add trace to the mode variable

    # Create radio buttons for mode selection
    rl_radio = Radiobutton(root, text="Reinforcement Learning", variable=mode_var, value="rl")
    search_radio = Radiobutton(root, text="Search-Based AI", variable=mode_var, value="search")
    human_radio = Radiobutton(root, text="Manual (Human Controls)", variable=mode_var, value="human")

    # Create a variable to store the selected rl_mode
    rl_mode_var = tk.StringVar(value="train")

    # Create radio buttons for rl_mode selection
    train_radio = Radiobutton(root, text="Train", variable=rl_mode_var, value="train")
    play_radio = Radiobutton(root, text="Play", variable=rl_mode_var, value="play")

    # Place rl_mode radio buttons
    train_radio.grid(row=11, column=0, sticky='nsew', padx=10, pady=5)
    play_radio.grid(row=12, column=0, sticky='nsew', padx=10, pady=5)

    # Create sliders for other parameters
    learning_rate_slider = Scale(root, label="Learning Rate", from_=0.0001, to=0.01, resolution=0.0001, orient="horizontal")
    discount_factor_slider = Scale(root, label="Discount Factor", from_=0.0, to=1.0, resolution=0.01, orient="horizontal")
    hidden_layers_slider = Scale(root, label="Hidden Layers", from_=1, to=5, orient="horizontal")
    epsilon_slider = Scale(root, label="Epsilon", from_=0.001, to=1.0, resolution=0.001, orient="horizontal")
    epsilon_decay_slider = Scale(root, label="Epsilon Decay", from_=0.9, to=1.0, resolution=0.001, orient="horizontal")
    epsilon_min_slider = Scale(root, label="Epsilon Min", from_=0.001, to=0.1, resolution=0.001, orient="horizontal")

    # Group sliders for easy show/hide
    sliders = [learning_rate_slider, discount_factor_slider, hidden_layers_slider, epsilon_slider, epsilon_decay_slider, epsilon_min_slider]

    # Set default values for sliders
    learning_rate_slider.set(0.00025)
    discount_factor_slider.set(0.9)
    hidden_layers_slider.set(2)
    epsilon_slider.set(1.0)
    epsilon_decay_slider.set(0.995)
    epsilon_min_slider.set(0.001)

    # Place radio buttons
    rl_radio.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)
    search_radio.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
    human_radio.grid(row=2, column=0, sticky='nsew', padx=10, pady=5)

    # Create a frame for the sliders
    sliders_frame = Frame(root)
    sliders_frame.grid(row=3, column=0, sticky='nsew', padx=10, pady=5)

    # Configure the sliders frame layout to auto-resize
    sliders_frame.grid_columnconfigure(0, weight=1)
    for i in range(6):  # Assuming 6 sliders
        sliders_frame.grid_rowconfigure(i, weight=1)

    # Pack sliders into the frame
    sliders = [learning_rate_slider, discount_factor_slider, hidden_layers_slider, epsilon_slider, epsilon_decay_slider, epsilon_min_slider]
    for slider in sliders:
        slider.grid(sticky='nsew', padx=10, pady=5)

    # Create a frame for the button to ensure it stays at the bottom
    button_frame = Frame(root)
    button_frame.grid(row=10, column=0, sticky='nsew', padx=10, pady=10)
    root.grid_rowconfigure(10, weight=0)  # This row will not expand

    # Run the game button
    run_button = Button(root, text="Run Game", command=run_game)
    run_button.grid(row=10, column=0, padx=10, pady=10, sticky='nsew')

    # Configure the grid layout to auto-resize
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(3, weight=1)

    root.mainloop()

if __name__ == "__main__":
    start_gui()