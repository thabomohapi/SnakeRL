import torch, numpy as np # type: ignore
import torch.nn as nn # type: ignore
import torch.optim as optim # type: ignore
import os

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class DQN(nn.Module):
    def __init__(self, input_size, hidden_layers, output_size) -> None:
        super().__init__()
        self.h_layers = []
        self.inputLayer = nn.Linear(input_size, hidden_layers[0])
        if len(hidden_layers) > 1:
            for i in range (len(hidden_layers) - 1):
                self.h_layers.append(nn.Linear(hidden_layers[i], hidden_layers[i + 1]).to(DEVICE))
        self.outputLayer = nn.Linear(hidden_layers[-1], output_size)
        self.to(DEVICE)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.to(DEVICE)  # Ensure input tensor is on the right device
        x = torch.relu(self.inputLayer(x))
        for layer in self.h_layers:
            x = torch.relu(layer(x))
        return self.outputLayer(x)
    
    def load(self, file_name: str = 'model.pth') -> None:
        model_folder_path = './model'
        file_name = os.path.join(model_folder_path, file_name)
        
        if os.path.isfile(file_name):
            self.load_state_dict(torch.load(file_name))
            self.to(DEVICE)
        else:
            print(f'No model file found at {file_name}. Starting from scratch.')
    
    def save(self, file_name: str = 'model.pth') -> None:
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

class Trainer:
    def __init__(self, model, lr, γ) -> None:
        self.lr = lr
        self.γ = γ
        self.model = model.to(DEVICE)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.loss_fn = nn.SmoothL1Loss()
        # self.loss_fn = nn.MSELoss()

    def train(self, state, action, reward, next_state, death) -> None:
        state = torch.tensor(np.array(state), dtype=torch.float32).to(DEVICE)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float32).to(DEVICE)
        action = torch.tensor(np.array(action), dtype=torch.long).to(DEVICE)
        reward = torch.tensor(np.array([reward]), dtype=torch.float32).to(DEVICE)

        # Ensure tensors have the correct shape for batch processing
        state = torch.unsqueeze(state, 0) if state.dim() == 1 else state
        next_state = torch.unsqueeze(next_state, 0) if next_state.dim() == 1 else next_state
        action = torch.unsqueeze(action, 0) if action.dim() == 1 else action
        reward = torch.unsqueeze(reward, 0) if reward.dim() == 1 else reward
        death = (death, ) if isinstance(death, bool) else death
        
        # get current state Q value
        prediction = self.model(state)
        target = prediction.clone()
        
        for i in range(len(death)):
            Q_new = reward[0][i]
            if not death[i]:  # Check if not dead
                Q_new = Q_new + (self.lr * (reward[0][i] + (self.γ * torch.max(self.model(next_state[i]).detach()) - Q_new)))
            # Assume action is a one-hot encoded tensor
            target[i][torch.argmax(action).item()] = Q_new

        self.optimizer.zero_grad()  # empty the gradients
        loss = self.loss_fn(target, prediction)
        loss.backward()
        self.optimizer.step()