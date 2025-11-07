from flask import Flask,request,jsonify
import torch
from torchvision import transforms
from PIL import Image
from model import SimpleCNN

app=Flask(__name__)
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device :",device)
model=SimpleCNN()
model.load_state_dict(torch.load("simple_cnn.pth", map_location=device))
model.to(device)

model.eval()

transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465),
                         (0.2023, 0.1994, 0.2010))
])

classes = ['plane', 'car', 'bird', 'cat', 'deer', 
           'dog', 'frog', 'horse', 'ship', 'truck']


@app.route('/predict',methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error':'no file uploader'}),400
    file=request.files['file']
    img=Image.open(file.stream).convert('RGB')
    img = transform(img).unsqueeze(0)
    
    with torch.no_grad():
        img=img.to(device)
        outputs=model(img)
        _,predicted=torch.max(outputs,1)
        label = classes[predicted.item()]

    return jsonify({'predict': label})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



    