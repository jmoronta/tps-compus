#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import torch.utils
import os

import shutil
import torchvision

import numpy as np

from torch import nn

import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

import sklearn
import pandas as pd
import random
import re

from torchvision import models, transforms
from math import floor
from PIL import Image, ImageEnhance
from google.colab import drive
from os import path


import tensorflow as tf
from tensorflow.keras.preprocessing import image


from google.colab.patches import cv2_imshow

import cv2
from PIL import Image

import torch

import random


from google.colab.patches import cv2_imshow


# # Montamos drive

# In[ ]:


# para encontrar una carpeta compartida hay que generar desde tu drive
# un acceso directo de la carpeta que se quiere encontrar, haciendo clic
# derecho sobre la carpeta y seleccionando "Añadir acceso directo a drive".

drive.mount('/content/drive')


# # Descargamos los datos

# In[ ]:


#@title Usuario kaggle

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

for i in ['0','1']:
  dir = '/content/img/' + i
  archivos = os.listdir(dir)
  for img in archivos:
    img_path = dir + '/' + img
    expresion = re.match(r'^([^_]*)', img).group(1)
    if int(expresion) in ids_train:
      shutil.move(img_path, '/content/train/' + i)
    elif int(expresion) in ids_val:
      shutil.move(img_path, '/content/val/' + i)
    else:
      shutil.move(img_path, '/content/test/' + i)


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


# # Demo

# In[ ]:


#@title ```Función predecir_cancer(folder_path, modelo)```

import torch.utils
import os

import shutil
import torchvision

import numpy as np

from torch import nn

import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

import sklearn
import pandas as pd
import random
import re

from torchvision import models, transforms
from math import floor
from PIL import Image, ImageEnhance
from google.colab import drive
from os import path


import tensorflow as tf
from tensorflow.keras.preprocessing import image


from google.colab.patches import cv2_imshow

import cv2
from PIL import Image

import torch

import random


from google.colab.patches import cv2_imshow


# Definir la función
def predecir_cancer(folder_path, modelo):
    
    # Elegir aleatoriamente 0 o 1
    true_label = random.randint(0,1)
    
    # Obtener la lista de todas las imágenes en la carpeta
    img_list = os.listdir(os.path.join(folder_path, str(true_label)))
    
    # Seleccionar una imagen aleatoria de la lista
    img_file = random.choice(img_list)    
    
    # Obtener la ruta completa de la imagen seleccionada
    path_img = os.path.join(os.path.join(folder_path, str(true_label)), img_file)
    
    # Obtener el patient_id
    patient = expresion = re.match(r'^([^_]*)', img_file).group(1)
    print(f'Patient_id = {patient}')
    print(35*'-')

    # Obtener el image_id
    image_id = resultado = re.search(r"_(.+)\.png$", img_file).group(1)
    print(f'Image_id = {image_id}')
    print(35*'-')

    if true_label == 1:
      label = 'cancer'
    else:
      label = 'no cancer'
    
    if modelo == 'resnet':

      # definimos carpeta donde guardamos el modelo
      folder = '/content/drive/MyDrive/BreastCancer/modelos/modelos22'
      # creamos una instancia del modelo
      # resnet = torchvision.models.resnet18(pretrained=True)
      # resnet.fc = nn.Linear(resnet.fc.in_features, 2)
      # y cargamos los parámetros
      #resnet.load_state_dict(torch.load(path.join(folder, 'ResNet3.pt'), map_location=torch.device('cpu')))
      # resnet.load_state_dict(torch.load(path.join(folder, 'ResNet3.pt')))
      
      # creamos una instancia del modelo
      resnet = torchvision.models.resnet18(pretrained=False)
      resnet.fc = nn.Linear(resnet.fc.in_features, 2)
      # y cargamos los parámetros
      resnet.load_state_dict(torch.load(path.join(folder, 'ResNet4.pt'), map_location=torch.device('cpu')))


      # Cargamos las imágenes
      img = cv2.imread(path_img)
      # Convertimos el array en una imagen Pillow
      image1 = Image.fromarray(img)
      #Definimos media y desvio de los datos de entrenamiento ya calculados
      train_means = [0.0020293, 0.0020293, 0.0020293]
      train_stds = [0.00269501, 0.00269501, 0.00269501]
      # Definimos transformaciones: Resize y ToTensor
      transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(train_means, train_stds)])

      # Hacemos la predicción
      pred = resnet(transform(image1).unsqueeze(0)).argmax(axis=1).numpy()
      pred = int(pred)
      predic_label = 'cancer' if pred == 1 else 'no cancer'
      print(f'Predicted label: {predic_label}')
      print(35*'-')
      print(f'True label: {label}')
      print(35*'-')
    
    elif modelo == 'vgg':
      vgg = tf.keras.models.load_model('/content/drive/MyDrive/BreastCancer/modelos/modelos22/05_AUC0.8-prepross.h5')
      img2 = image.load_img(path_img, target_size=(224, 224))

      x = image.img_to_array(img2)
      x = np.expand_dims(x, axis=0)

      
      predictions = vgg.predict(x, verbose=0)

      pred = 1 if predictions[0] > 0.5 else 0
      predic_label = 'cancer' if pred == 1 else 'no cancer'
      print(f'Predicted label: {predic_label}')
      print(35*'-')
      print(f'True label: {label}')
      print(35*'-')

    # Convertimos las imágenes a RGB
    img = cv2.imread(path_img)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2_imshow(img)   


# In[ ]:


test_folder = '/content/test'


# In[ ]:


predecir_cancer(test_folder, 'resnet')


# In[ ]:


predecir_cancer(test_folder, 'vgg')

