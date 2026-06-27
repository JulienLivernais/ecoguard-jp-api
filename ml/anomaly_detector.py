import torch
import torch.nn as nn

class AnomalyDetector(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=1,
            hidden_size=32,
            num_layers=2,
            batch_first=True
        )
        self.fc = nn.Linear(32, 1)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_output = lstm_out[:, -1, :]
        return self.fc(last_output)

    def predict(self, values: list) -> float:
        x = torch.tensor(values, dtype=torch.float32).unsqueeze(0).unsqueeze(-1)
        self.eval()
        with torch.no_grad():
            score = self.forward(x)
            return score.item()


