import torch, numpy as np # type: ignore
import torch.nn as nn # type: ignore
import torch.optim as optim # type: ignore
import torch.nn.functional as functional # type: ignore
import os

class DQN(nn.Module):
    def __init__(self, input_size, hidden_size1, hidden_size2, hidden_size3, output_size) -> None:
        super().__init__()
        self.layer1 = nn.Linear(input_size, hidden_size1)
        self.layer2 = nn.Linear(hidden_size1, hidden_size2)
        self.layer3 = nn.Linear(hidden_size2, hidden_size3)
        self.layer4 = nn.Linear(hidden_size3, output_size)

    def forward(self, x):
        x = functional.relu(self.layer1(x))
        x = functional.relu(self.layer2(x))
        x = functional.relu(self.layer3(x))
        x = self.layer4(x)
        return x
    
    def save(self, file_name = 'model.pth') -> None:
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

class Trainer:
    def __init__(self, model, lr, γ) -> None:
        self.lr = lr
        self.γ = γ
        self.model = model
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.loss_fn = nn.SmoothL1Loss()

    def train(self, state, action, reward, next_state, death) -> None:
        state = torch.tensor(np.array(state), dtype=torch.float32)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float32)
        action = torch.tensor(np.array(action), dtype=torch.long)
        reward = torch.tensor(np.array([reward]), dtype=torch.float32)

        # Ensure tensors have the correct shape for batch processing
        state = torch.unsqueeze(state, 0) if state.dim() == 1 else state
        next_state = torch.unsqueeze(next_state, 0) if next_state.dim() == 1 else state
        action = torch.unsqueeze(action, 0) if action.dim() == 1 else action
        reward = torch.unsqueeze(reward, 0) if reward.dim() == 1 else reward
        death = (death, ) if isinstance(death, bool) else death

        # print(f"State: {state}")
        # print(f"Action: {action}")
        # print(f"Reward: {reward}")
        # print(f"Death: {death}")
        
        # get current state Q value
        prediction = self.model(state)
        target = prediction.clone()
        # print(f"Target = {target}")
        for i in range(len(death)):
            Q_new = reward[0][i]
            if not death[i]:  # Check if not dead
                Q_new = reward[0][i] + self.γ * torch.max(self.model(next_state[i]))
            # Assume action is a one-hot encoded tensor
            # print(f"Q_new = {Q_new}")
            # print(target[i][torch.argmax(action[i]).item()])
            target[i][torch.argmax(action[i]).item()] = Q_new

        self.optimizer.zero_grad()  # empty the gradients
        loss = self.loss_fn(target, prediction)
        loss.backward()
        self.optimizer.step()