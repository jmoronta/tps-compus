#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from torchvision.datasets import ImageFolder
from torch.utils.data import Subset
import torch.utils
import os

import tempfile
import uuid
import shutil
import torchvision

import numpy as np
import pickle

from torch import nn

import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

import sklearn
import pandas as pd
import random
import re

from torchvision import transforms
from math import floor


# # Descargamos los datos

# In[ ]:


get_ipython().system('mkdir ~/.kaggle #crea la carpeta .kaggle en tu directorio raiz')
get_ipython().system('echo \'{"username":"rodrigorobert","key":"97ed5e903ef16e8dfa245ebe1ab8351b"}\' > ~/.kaggle/kaggle.json #escribe las credenciales de la API de kaggle en kaggle.json')
get_ipython().system('chmod 600 ~/.kaggle/kaggle.json  # establecer permisos')


# In[ ]:


get_ipython().system('kaggle datasets download -d gauravduttakiit/mammography-breast-cancer-detection')


# In[ ]:


get_ipython().system("unzip '/content/mammography-breast-cancer-detection.zip'")


# In[ ]:


train = pd.read_csv('/content/train.csv')
train.head()


# In[ ]:


# Obtenemos los ids de los pacientes y los mezclamos aleatoriamente

ids_patient = train['patient_id'].unique()
random.seed(4)
random.shuffle(ids_patient)
ids_patient


# In[ ]:


# Separamos los pacientes en 3 subconjuntos
ids_train = ids_patient[:floor(len(ids_patient) * 0.7)]
ids_val = ids_patient[floor(len(ids_patient)*0.7)+1:floor(len(ids_patient)*0.9)]
ids_test = ids_patient[floor(len(ids_patient) * 0.9)+1:]


# In[ ]:


# Renombramos las carpetas train y test que se descargan de Kaggle
os.rename('/content/train', '/content/img')
os.rename('/content/test', '/content/img_test')


# In[ ]:


# Crear las carpetas para los conjuntos de entrenamiento, validación y prueba
os.makedirs('/content/train/0', exist_ok=True)
os.makedirs('/content/train/1', exist_ok=True)
os.makedirs('/content/val/0', exist_ok=True)
os.makedirs('/content/val/1', exist_ok=True)
os.makedirs('/content/test/0', exist_ok=True)
os.makedirs('/content/test/1', exist_ok=True)


# In[ ]:


# Movemos las imagenes a las carpetas de forma de que las imagenes de
# un mismo paciente queden todas en train,  val o test


dir0 = '/content/img/0'
dir1 = '/content/img/1'
archivos0 = os.listdir(dir0)
archivos1 = os.listdir(dir1)
for i,img in enumerate(archivos1):
  img_path0 = dir0 + '/' + archivos0[i]
  img_path1 = dir1 + '/' + img
  expresion = re.match(r'^([^_]*)', img).group(1)
  if int(expresion) in ids_train:
    shutil.move(img_path0, '/content/train/0')
    shutil.move(img_path1, '/content/train/1')
  elif int(expresion) in ids_val:
    shutil.move(img_path0, '/content/val/0')
    shutil.move(img_path1, '/content/val/1')
  else:
    shutil.move(img_path0, '/content/test/0')
    shutil.move(img_path1, '/content/test/1')


# In[ ]:


# Establecemos nombres de carpetas con datos
folders = ['train','val','test']

# Establecemos directorio raiz
root = "/content/"

# Establecemos lista para guardar recuento
count_data = []

for folder in folders:
  count_0 = 0
  count_1 = 0
  dir = root + folder + '/0'
  # Recorremos cada elemento en el directorio
  for path in os.listdir(dir):
    # Comprobamos si el elemento actual es un archivo
    if os.path.isfile(os.path.join(dir, path)):
      # Si es un archivo, aumentamos el contador de imágenes en 1
      count_0 += 1
  dir = root + folder + '/1'
  for path in os.listdir(dir):
    # Comprobamos si el elemento actual es un archivo
    if os.path.isfile(os.path.join(dir, path)):
      # Si es un archivo, aumentamos el contador de imágenes en 1
      count_1 += 1
  count_data.append((count_0,count_1))

count_data


# In[ ]:


# Calculamos el porcentaje en train-val-test
total = sum(count_data[0]) + sum(count_data[1]) + sum(count_data[2])
print(f'Train: {round(sum(count_data[0]) / total,2)}')
print(f'Val: {round(sum(count_data[1]) / total,2)}')
print(f'Test: {round(sum(count_data[2]) / total,2)}')


# # Resnet preentrenada sin data augmentation

# ## Armamos dataloader y normalizamos

# In[ ]:


# Aplicaamos transformaciones: Resize y ToTensor
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()])


# Establecemos directorios
train_dir = '/content/train'
val_dir = '/content/val'
test_dir = '/content/test'


# Creamos conjuntos de datos usando la clase Subset
train_dataset = ImageFolder(train_dir, transform=transform)
val_dataset = ImageFolder(val_dir, transform=transform)
test_dataset = ImageFolder(test_dir, transform=transform)

# Creamos cargadores de datos para cada conjunto de datos
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=128, shuffle=True)
val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=128)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=128)


# In[ ]:


next(iter(train_loader))[0].shape


# In[ ]:


# asumimos que las imágenes están en formato RGB
# asumimos que tienen una forma de (batch_size, 3, height, width)

# Recorre el dataloader para acumular los valores de píxeles
channel_means = np.zeros(3)
channel_stds = np.zeros(3)
n_images = 0

for batch in train_loader:
    images, _ = batch
    batch_means = np.mean(images.numpy(), axis=(0, 2, 3))
    batch_stds = np.std(images.numpy(), axis=(0, 2, 3))

    channel_means += batch_means
    channel_stds += batch_stds
    n_images += images.shape[0]

# Calcula la media y la desviación estándar del conjunto completo
train_means = channel_means / n_images
train_stds = channel_stds / n_images

print("Media: ", train_means)
print("Desviación estándar: ", train_stds)


# In[ ]:


# Aplica la normalización a las imágenes en el DataLoader
normalize = torchvision.transforms.Normalize(train_means, train_stds)

for images, labels in train_loader:
    # Aplica la normalización a cada imagen en el batch
    normalized_images = normalize(images)

for images, labels in val_loader:
    # Aplica la normalización a cada imagen en el batch
    normalized_images = normalize(images)

for images, labels in test_loader:
    # Aplica la normalización a cada imagen en el batch
    normalized_images = normalize(images)


# ## Entrenamiento y evaluación

# In[ ]:


def accuracy(y_hat, y):
    """Compute the number of correct predictions."""
    if len(y_hat.shape) > 1 and y_hat.shape[1] > 1:
        y_hat = y_hat.argmax(axis=1)
    cmp = y_hat.type(y.dtype) == y
    return float(cmp.type(y.dtype).sum())


# In[ ]:


finetune_net1 = torchvision.models.resnet18(pretrained=True)
finetune_net1.fc = nn.Linear(finetune_net1.fc.in_features, 2)
nn.init.xavier_uniform_(finetune_net1.fc.weight);


# In[ ]:


# Si `param_group=True`, los parámetros del modelo en la capa de salida se
# actualizarán usando una tasa de aprendizaje diez veces mayor
def train_fine_tuning(model, train_iter, val_iter, learning_rate, batch_size=128,
                      num_epochs=10, param_group=True):
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    loss = nn.CrossEntropyLoss(reduction="none")
    if param_group:
        params_1x = [param for name, param in model.named_parameters()
             if name not in ["fc.weight", "fc.bias"]]
        trainer = torch.optim.SGD([{'params': params_1x},
                                   {'params': model.fc.parameters(),
                                    'lr': learning_rate * 10}],
                                lr=learning_rate, weight_decay=0.001)
    else:
        trainer = torch.optim.Adam(model.parameters(), lr=learning_rate,
                                  weight_decay=0.001)
    model.to(device)
    list_acc_train = []
    list_acc_val = []
    list_loss_train = []
    list_loss_val = []
    for epoch in range(num_epochs):
      L_train = 0.0
      N_train = 0
      Acc_train = 0.0
      for X, y in train_iter:
          X, y = X.to(device), y.to(device)
          l = loss(model(X),y)
          trainer.zero_grad()
          l.mean().backward()
          trainer.step()
          L_train += l.sum()
          N_train += l.numel()
          Acc_train += accuracy(model(X), y)

      L_val = 0.0
      N_val = 0
      Acc_val = 0.0
      for X, y in val_iter:
        with torch.no_grad():
            X, y = X.to(device), y.to(device)
            l = loss(model(X),y)
            L_val += l.sum()
            N_val += l.numel()
            Acc_val += accuracy(model(X), y)
          
      list_acc_train.append(Acc_train/N_train)
      list_acc_val.append(Acc_val/N_val)
      list_loss_train.append(L_train/N_train)
      list_loss_val.append(L_val/N_val)
      print(f'epoch {epoch + 1}')
      print(f'loss train: {(L_train/N_train):f}, Acc train: {(Acc_train/N_train):f}')
      print(f'loss val: {(L_val/N_val):f}, Acc val: {(Acc_val/N_val):f}')
      print(70*'=')
    return list_acc_train, list_acc_val, list_loss_train, list_loss_val


# In[ ]:


acc_train, acc_val, loss_train, loss_val = train_fine_tuning(finetune_net1, train_loader, val_loader, 0.00001)


# In[ ]:


# Graficos de la loss function y accuracy por epocas

fig, axs = plt.subplots(1, 2)
axs[0].plot([t.item() for t in loss_train], label = 'Training')
axs[0].plot([t.item() for t in loss_val], '--', label = 'Validation')
axs[0].legend()
axs[0].set_title('Loss-Function')
axs[1].plot(acc_train, label = 'Training')
axs[1].plot(acc_val, '--', label = 'Validation')
axs[1].legend()
axs[1].set_title('Accuracy')
plt.show()


# In[ ]:


#Graficamos la matriz de confusion normalizada por fila.

prediccion = []
etiqueta = []
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
for X, y in val_loader:
  X, y = X.to(device), y.to(device)
  prediccion += list(finetune_net1(X).argmax(axis=1).to('cpu').numpy())
  etiqueta += list(y.to('cpu').numpy())

CM = confusion_matrix(etiqueta, prediccion, normalize='all')

plt.figure(figsize=(12,7))
sns.set(font_scale=1.2) # for label size
ax = plt.axes()
sns.heatmap(CM, annot=True, annot_kws={"size": 12}, linewidths=.5, cmap="rocket_r")
ax.set_title('Matriz de Confusión', fontsize = 20)
plt.xlabel('Predicted Label', fontsize = 15)
plt.ylabel('True Label', fontsize = 15)
plt.show()


# In[ ]:


fpr, tpr, thresholds = sklearn.metrics.roc_curve(etiqueta, prediccion, pos_label=None, sample_weight=None, drop_intermediate=True)
auc = sklearn.metrics.roc_auc_score(etiqueta, prediccion)


# In[ ]:


# Grafica la curva ROC

plt.plot(fpr, tpr, label='Curva ROC (AUC = {:.2f})'.format(auc))
plt.plot([0, 1], [0, 1], 'k--', label='Clasificador aleatorio')
plt.xlabel('Tasa de falsos positivos')
plt.ylabel('Tasa de verdaderos positivos')
plt.title('Curva ROC')
plt.legend(loc='lower right')
plt.show()


# In[ ]:


auc

