from PIL import Image
from torchvision import  transforms
import torch
import torch.nn as nn
import torch.nn.functional as F

# ======================
# 模型定义
# ======================
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        # 输入: [3, 32, 32]
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)  # 降维一半
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))   # [32,16,16]
        x = self.pool(F.relu(self.conv2(x)))   # [64,8,8]
        x=torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# ======================
# 模型加载
# ======================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

model = SimpleCNN().to(device)
model.load_state_dict(torch.load("simple_cnn.pth", map_location=device))
model.eval()

# ======================
# 数据与推理
# ======================
transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465),
                         (0.2023, 0.1994, 0.2010))
])



img = Image.open("CIFAR_sample.png").convert("RGB")  
img = transform(img).unsqueeze(0).to(device)

with torch.no_grad():
    output = model(img)
    _, predicted = torch.max(output, 1)

classes = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck"
]

print(f"Predicted: {classes[predicted.item()]} ({predicted.item()}) ")
