import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torchvision.transforms as transforms

# CNN simples para extrair vetor da íris
class IrisCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.fc = nn.Linear(32*16*16, 128)  # vetor de 128 dimensões

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        x = nn.functional.normalize(x, p=2, dim=1)
        return x

# Instancia o modelo
model = IrisCNN()
model.eval()

def extrair_vetor_cnn(caminho_imagem):
    # Carrega imagem e converte para escala de cinza
    img = Image.open(caminho_imagem).convert('L')
    transform = transforms.Compose([
        transforms.Resize((64,64)),
        transforms.ToTensor()
    ])
    x = transform(img).unsqueeze(0)
    with torch.no_grad():
        vetor = model(x).numpy()[0]
    return ','.join(map(str, vetor))
