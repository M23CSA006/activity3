
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nnpi
import torch.optim as optim
from torchvision import models
import matplotlib.pyplot as plt

# Check if CUDA is available
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Define data transforms and download STL10 dataset
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

trainset = torchvision.datasets.STL10(root='./data', split='train', download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=32, shuffle=True)

testset = torchvision.datasets.STL10(root='./data', split='test', download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=32, shuffle=False)

# Load pre-trained ResNet50 model
model = models.resnet50(pretrained=True)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 10)  # 10 classes in STL10

model = model.to(device)

# Define loss function and optimizers
criterion = nn.CrossEntropyLoss()

optimizers = {
    'Adam': optim.Adam(model.parameters(), lr=0.001),
    'Adagrad': optim.Adagrad(model.parameters(), lr=0.01),
    'Adadelta': optim.Adadelta(model.parameters(), lr=1.0),
}

# Training loop
epochs = 5
losses = {optimizer_name: [] for optimizer_name in optimizers}
accuracies = {optimizer_name: [] for optimizer_name in optimizers}

for optimizer_name, optimizer in optimizers.items():
    print(f"Training with {optimizer_name} optimizer...")
    for epoch in range(epochs):  # Loop over epochs
        running_loss = 0.0    # Initialize running loss
        correct = 0   # Initialize number of correct predictions
        total = 0  # Initialize total number of predictions

        for inputs, labels in trainloader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

        epoch_loss = running_loss / len(trainloader)
        epoch_accuracy = 100 * correct / total

        losses[optimizer_name].append(epoch_loss)
        accuracies[optimizer_name].append(epoch_accuracy)

        print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss:.4f}, Accuracy: {epoch_accuracy:.2f}%")

# Plotting training loss and accuracy curves
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
for optimizer_name, loss_values in losses.items():
    plt.plot(range(1, epochs + 1), loss_values, label=optimizer_name)
plt.xlabel('Epochs') # Set x-axis label
plt.ylabel('Training Loss') # Set y-axis label
plt.title('Training Loss Curves') # Set title
plt.legend() # show legend

plt.subplot(1, 2, 2)
for optimizer_name, accuracy_values in accuracies.items():
    plt.plot(range(1, epochs + 1), accuracy_values, label=optimizer_name)
plt.xlabel('Epochs')
plt.ylabel('Training Accuracy (%)')
plt.title('Training Accuracy Curves')
plt.legend()

plt.tight_layout()
plt.show()

# Test the model and report top-5 accuracy
model.eval()
top5_correct = 0
total = 0

with torch.no_grad():
    for inputs, labels in testloader:
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        _, predicted = outputs.topk(5, 1, True, True)
        total += labels.size(0)
        top5_correct += predicted.eq(labels.view(-1, 1).expand_as(predicted)).sum().item()

top5_accuracy = 100 * top5_correct / total # Calculate top-5 accuracy
print(f"Final Top-5 Test Accuracy: {top5_accuracy:.2f}%") # Print top-5 accuracy