import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np

# Define the neural network model for approximating Q-values.
class DQN(nn.Module):
    def __init__(self, input_size, output_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_size)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Experience replay buffer.
class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []
    
    def push(self, state, action, reward, next_state, done):
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)
    
    def __len__(self):
        return len(self.buffer)

# ... (other parts of ai_dqn.py remain unchanged)

class DeepQAgent:
    def __init__(self, player, lr=0.001, gamma=0.9, epsilon=0.2, buffer_capacity=10000, batch_size=32):
        self.player = player
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.batch_size = batch_size
        self.input_size = 24  # Number of board positions.
        self.output_size = 24  # Possible placing actions.
        
        self.policy_net = DQN(self.input_size, self.output_size)
        self.target_net = DQN(self.input_size, self.output_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.lr)
        self.replay_buffer = ReplayBuffer(buffer_capacity)
        self.steps_done = 0
        self.update_target_every = 1000  # Update target network every 1000 steps.
        
        # Variables to store last state information.
        self.last_state = None
        self.last_positions = None
        self.last_action = None

    def get_state_tensor(self, board_state, positions):
        state_list = []
        for pos in sorted(positions.keys()):
            val = board_state[pos]
            if val is None:
                state_list.append(0.0)
            elif val == self.player:
                state_list.append(1.0)
            else:
                state_list.append(-1.0)
        return torch.tensor(state_list, dtype=torch.float32).unsqueeze(0)
    
    def select_action(self, board_state, positions):
        state = self.get_state_tensor(board_state, positions)
        if random.random() < self.epsilon:
            empty_indices = [i for i, pos in enumerate(sorted(positions.keys())) if board_state[pos] is None]
            action = random.choice(empty_indices) if empty_indices else None
        else:
            with torch.no_grad():
                q_values = self.policy_net(state).squeeze(0).numpy()
                # Mask non-empty positions.
                for i, pos in enumerate(sorted(positions.keys())):
                    if board_state[pos] is not None:
                        q_values[i] = -float('inf')
                action = int(np.argmax(q_values))
        # Save current board state and positions for later use.
        self.last_state = board_state.copy()  # copy to preserve current state
        self.last_positions = positions
        self.last_action = action
        return action

    def store_transition(self, board_state, positions, action, reward, next_board_state, done):
        state_tensor = self.get_state_tensor(board_state, positions)
        next_state_tensor = self.get_state_tensor(next_board_state, positions)
        self.replay_buffer.push(state_tensor, action, reward, next_state_tensor, done)

    def optimize_model(self):
        if len(self.replay_buffer) < self.batch_size:
            return
        transitions = self.replay_buffer.sample(self.batch_size)
        batch_state, batch_action, batch_reward, batch_next_state, batch_done = zip(*transitions)
        
        batch_state = torch.cat(batch_state)
        batch_action = torch.tensor(batch_action, dtype=torch.int64).unsqueeze(1)
        batch_reward = torch.tensor(batch_reward, dtype=torch.float32).unsqueeze(1)
        batch_next_state = torch.cat(batch_next_state)
        batch_done = torch.tensor(batch_done, dtype=torch.float32).unsqueeze(1)
        
        current_q = self.policy_net(batch_state).gather(1, batch_action)
        next_q = self.target_net(batch_next_state).max(1)[0].detach().unsqueeze(1)
        expected_q = batch_reward + self.gamma * next_q * (1 - batch_done)
        
        loss = nn.MSELoss()(current_q, expected_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        self.steps_done += 1
        if self.steps_done % self.update_target_every == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

    def update(self, reward, board_state, positions):
        """
        Called at game end to record a terminal transition with the given reward.
        The current board_state and positions (global) are used as the terminal state.
        """
        if self.last_state is None or self.last_action is None:
            return  # Nothing to update
        self.store_transition(self.last_state, self.last_positions, self.last_action, reward, board_state, True)
        self.optimize_model()

    def get_q_values(self, board_state, positions):
        """
        Returns raw Q-values for the current board state.
        Useful for visualizing the agent's preferences.
        """
        state_tensor = self.get_state_tensor(board_state, positions)
        with torch.no_grad():
            q_values = self.policy_net(state_tensor).squeeze(0).numpy()
        return q_values
