import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque
from ai_environment import TradingEnvironment

# Neural Network for DQN
class DQN(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(DQN, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )
    
    def forward(self, x):
        return self.fc(x)

class Agent:
    def __init__(self, state_dim, action_dim):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.memory = deque(maxlen=5000)
        self.gamma = 0.99 # Higher gamma for long-term vision
        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.997
        
        self.model = DQN(state_dim, action_dim)
        self.target_model = DQN(state_dim, action_dim)
        self.update_target_model()
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.0005) # Slower LR for precision
        self.criterion = nn.MSELoss()

    def update_target_model(self):
        """Copies weights from model to target_model."""
        self.target_model.load_state_dict(self.model.state_dict())

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_dim)
        state = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            q_values = self.model(state)
        return torch.argmax(q_values).item()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        
        states = torch.FloatTensor(np.array([s for s, a, r, n, d in minibatch]))
        actions = torch.LongTensor([a for s, a, r, n, d in minibatch])
        rewards = torch.FloatTensor([r for s, a, r, n, d in minibatch])
        next_states = torch.FloatTensor(np.array([n for s, a, r, n, d in minibatch]))
        dones = torch.FloatTensor([d for s, a, r, n, d in minibatch])

        # Current Q values
        q_values = self.model(states)
        current_q = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)

        # Target Q values using Target Network (Classic DQN)
        with torch.no_grad():
            next_q_values = self.target_model(next_states)
            max_next_q = next_q_values.max(1)[0]
            targets = rewards + (1 - dones) * self.gamma * max_next_q

        loss = self.criterion(current_q, targets)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

def train():
    env = TradingEnvironment("SOLUSDT_15m_historical.csv")
    state_dim = 7 # [price, ema9, ema21, rsi, balance, inventory, progress]
    action_dim = 3 # HOLD, BUY, SELL
    agent = Agent(state_dim, action_dim)
    episodes = 200 # Increased for precision
    batch_size = 64
    target_update_freq = 10 # Update target every 10 episodes

    print("🚀 Starting AI Training (Reinforcement Learning)...")
    for e in range(episodes):
        state = env.reset()
        episode_reward = 0
        for time_step in range(300):
            action = agent.act(state)
            next_state, reward, done, info = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            episode_reward += reward
            if done:
                break
            if len(agent.memory) > batch_size and time_step % 20 == 0:
                agent.replay(batch_size)
        
        if e % target_update_freq == 0:
            agent.update_target_model()
        
        print(f"Episode: {e+1}/{episodes} | Reward: {episode_reward:.2f} | Net Worth: {info['net_worth']:.2f} | Epsilon: {agent.epsilon:.2f}")
    
    # Save the trained model
    torch.save(state_dim, "trading_agent_metadata.pth") # Save metadata
    torch.save(agent.model.state_dict(), "trading_agent.pth")
    print("💾 AI Model Saved: trading_agent.pth")

if __name__ == "__main__":
    train()
