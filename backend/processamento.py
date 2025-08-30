from PIL import Image
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import torch.nn as nn

# --- ATENÇÃO: CÓDIGO ATUALIZADO PARA CORRIGIR O AVISO DE 'pretrained' ---
# Carrega o modelo ResNet-18 com a nova sintaxe de 'weights'
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model = nn.Sequential(*list(model.children())[:-1]) # Remove a última camada
model.eval() # Coloca o modelo em modo de avaliação

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# --- FUNÇÃO ATUALIZADA E MAIS ROBUSTA ---
def extrair_vetor(caminho_imagem):
    """
    Recebe o caminho de uma imagem, processa com o modelo e retorna um vetor
    em formato de string limpa, apenas com números e vírgulas.
    """
    try:
        img = Image.open(caminho_imagem).convert("RGB")
        img_t = transform(img)
        batch_t = torch.unsqueeze(img_t, 0)

        with torch.no_grad():
            vetor_tensor = model(batch_t)
        
        # CORREÇÃO: Garante que o tensor seja convertido para um formato 1D (vetor)
        # e depois para um array NumPy antes de virar string.
        vetor_numpy = vetor_tensor.squeeze().flatten().numpy()
        
        # Converte cada número float no array para string e junta com vírgulas
        return ','.join(vetor_numpy.astype(str))

    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
        return None