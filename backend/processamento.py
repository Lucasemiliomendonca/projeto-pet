from PIL import Image
import torch
import torchvision.transforms as transforms
import torchvision.models as models
import torch.nn as nn

model = models.resnet18(pretrained=True)
model = nn.Sequential(*list(model.children())[:-1])
model.eval()

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def extrair_vetor(caminho_imagem):
    try:
        img = Image.open(caminho_imagem).convert("RGB")
        img_t = transform(img)
        batch_t = torch.unsqueeze(img_t, 0)
        
        with torch.no_grad():
            vetor = model(batch_t)
        vetor_plano = torch.flatten(vetor).numpy()
        
        return ','.join(map(str, vetor))
    
    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
        return None
    