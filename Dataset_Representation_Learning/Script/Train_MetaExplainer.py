import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_add_pool
# from torch_geometric.data import DataLoader
import argparse
import os
import sys
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import numpy as np
from math import sqrt
from statistics import mean
import torch_geometric
from torch_geometric.datasets import TUDataset
import torch
import torch.nn as nn
from torch.nn.parameter import Parameter
from torch_geometric.nn import GCNConv
import torch.nn.functional as F
from torch.nn import Linear, ReLU, Sequential
from sklearn import metrics
from scipy.spatial.distance import hamming
import statistics
import pandas
import csv
from time import perf_counter
from torch_geometric.nn import GCNConv, global_mean_pool
from torch_geometric.loader import DataLoader
import torch_geometric.nn as gnn
from torch.autograd import graph
from typing import Any, Dict, Optional, Union
from IPython.core.display import deepcopy
from torch_geometric.nn import MessagePassing
import copy
from importlib import reload
import pickle
from sklearn.preprocessing import label_binarize
from tqdm.auto import tqdm
from torch_geometric.data import Data, Batch, Dataset


import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

directory_x = ("/data/cs.aau.dk/ey33jw/Explainability_Methods/Dataset_Creation_for_MetaExplainer/Experimental Results/" +
               "X.pt")
directory_y = ("/data/cs.aau.dk/ey33jw/Explainability_Methods/Dataset_Creation_for_MetaExplainer/Experimental Results/" +
               "Y.pt")
X_list = torch.load(directory_x)
Y_list = torch.load(directory_y)

X_data = torch.stack(X_list).float()
Y_data = torch.stack(Y_list).float()

if Y_data.dim() > 1 and Y_data.size(1) > 1:
    Y_data = torch.argmax(Y_data, dim=1)

X_train, X_test, Y_train, Y_test = train_test_split(X_data, Y_data, test_size=0.2, random_state=42, shuffle=True)

class MetaExplainer(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(MetaExplainer, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

input_size = X_train.shape[1]
hidden_size = 64
output_size = len(torch.unique(Y_data))

meta_explainer = MetaExplainer(input_size, hidden_size, output_size)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(meta_explainer.parameters(), lr=0.001)

num_epochs = 500
batch_size = 32

train_dataset = torch.utils.data.TensorDataset(X_train, Y_train)
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

test_dataset = torch.utils.data.TensorDataset(X_test, Y_test)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

epoch_loss_list = []
epoch_accuracy_list = []
test_loss_list = []
test_accuracy_list = []

for epoch in range(num_epochs):
    meta_explainer.train()
    total_loss = 0
    correct = 0
    total = 0

    for batch_X, batch_Y in train_loader:
        outputs = meta_explainer(batch_X)
        loss = criterion(outputs, batch_Y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        correct += (predicted == batch_Y).sum().item()
        total += batch_Y.size(0)

    avg_loss = total_loss / len(train_loader)
    accuracy = 100 * correct / total

    epoch_loss_list.append(avg_loss)
    epoch_accuracy_list.append(accuracy)

    if (epoch + 1) % 10 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%')

meta_explainer.eval()
test_loss = 0
test_correct = 0
test_total = 0

with torch.no_grad():
    for test_X, test_Y in test_loader:
        test_outputs = meta_explainer(test_X)
        test_loss += criterion(test_outputs, test_Y).item()

        _, test_predicted = torch.max(test_outputs, 1)
        test_correct += (test_predicted == test_Y).sum().item()
        test_total += test_Y.size(0)

avg_test_loss = test_loss / len(test_loader)
test_accuracy = 100 * test_correct / test_total

test_loss_list.append(avg_test_loss)
test_accuracy_list.append(test_accuracy)

print(f'Test Loss: {avg_test_loss:.4f}, Test Accuracy: {test_accuracy:.2f}%')

epochs = range(1, num_epochs + 1)

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(epochs, epoch_loss_list, 'b', label='Training Loss')
plt.title('Training Loss', fontsize=22)
plt.xlabel('Epochs', fontsize=20)
plt.ylabel('Loss', fontsize=18, labelpad=5)
plt.legend(fontsize=18)
plt.tick_params(axis='both', which='major', labelsize=14)

plt.subplot(1, 2, 2)
plt.plot(epochs, epoch_accuracy_list, 'r', label='Training Accuracy')
plt.title('Training Accuracy', fontsize=22)
plt.xlabel('Epochs', fontsize=20)
plt.ylabel('Accuracy (%)', fontsize=18, labelpad=2)
plt.legend(fontsize=18)
plt.tick_params(axis='both', which='major', labelsize=14)

directory_plot = ("/data/cs.aau.dk/ey33jw/Explainability_Methods/Dataset_Creation_for_MetaExplainer/Experimental Results/MetaExplaienr_Accuracy.pdf")
plt.savefig(directory_plot)
# plt.show()
plt.close()
