#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('pip install kaggle #instalamos la libreria kaggle')
get_ipython().system('pip install matplotlib opencv-python watermark')


# In[ ]:


get_ipython().system('pip install matplotlib opencv-python watermark')


# In[ ]:


#importamos las librería que utilizaremos

import shutil
import pandas as pd
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

from google.colab.patches import cv2_imshow

from  scipy.stats import chi2_contingency


# In[ ]:


get_ipython().system("mkdir '/content/kaggle' #creamos la carpeta .kaggle en el directorio raiz")
get_ipython().system('echo \'{"username":"mauronatale","key":"2436f5f5ec631b7b7566bea54362f56b"}\' > ~/.kaggle/kaggle.json #escribimos las credenciales de la API de kaggle en kaggle.json')
get_ipython().system('chmod 600 ~/.kaggle/kaggle.json  #establecemos permisos')


# In[ ]:


#descargamos el dataset de kaggle
get_ipython().system('kaggle datasets download -d gauravduttakiit/mammography-breast-cancer-detection')


# In[ ]:


#dezipeamos el dataset
get_ipython().system("unzip '/content/mammography-breast-cancer-detection.zip'")


# In[ ]:


#movemos los archivos a la carpeta .kaggle
shutil.move('mammography-breast-cancer-detection.zip', '/content/kaggle/mammography-breast-cancer-detection.zip')
shutil.move('test', '/content/kaggle/test')
shutil.move('train', '/content/kaggle/train')
shutil.move('test.csv', '/content/kaggle/test.csv')
shutil.move('train.csv', '/content/kaggle/train.csv')


# # Análisis exploratorio de los datos (EDA)
# 

# A continuación realizaremos el análisis exploratorio de los datos para el dataset [Mammography Breast Cancer Detection](https://www.kaggle.com/datasets/gauravduttakiit/mammography-breast-cancer-detection?select=train.csv&group=bookmarked) extraido de Kaggle y provistos por la 
# Sociedad Radiológica de América del Norte (RSNA).
# 
# La RSNA es una organización sin fines de lucro que representa 31 subespecialidades radiológicas de 145 países de todo el mundo. RSNA promueve la excelencia en la atención al paciente y la prestación de atención médica a través de la educación, la investigación y la innovación tecnológica.

# ## Análisis datos de entrenamiento

# In[ ]:


train = pd.read_csv('/content/kaggle/train.csv')
train.head()


# In[ ]:


train.info()


# Explicación de las columnas: 
# 
# `site_id` - Código de identificación del hospital de origen.  
# `patient_id` - Código de identificación del paciente.  
# `image_id` - Código de identificación de la imagen.  
# `laterality` - Si la imagen es del seno izquierdo o derecho.  
# `view` - La orientación de la imagen. El valor predeterminado para un examen de detección es capturar dos vistas por seno.  
# `age` - La edad del paciente en años. **Hay datos faltantes**.  
# `implant` - Si la paciente tenía o no implantes mamarios. El sitio 1 solo proporciona información sobre los implantes mamarios a nivel del paciente, no a nivel del seno.  
# `machine_id` - Un código de identificación para el dispositivo de imágenes.  
# `prediction_id` - El ID de la fila de envío coincidente. Varias imágenes compartirán el mismo ID de predicción. <font color=magenta>Solo en test.</font>  
# `cancer` - Si la mama fue o no positiva para cáncer. Target. <font color=magenta>Solo en train.</font>

# La única feature que tiene datos faltantes es **age**.

# In[ ]:


#cantidad de imágenes
train.shape


# In[ ]:


# Inicializar el contador de imágenes en 0
initial_count = 0

# Establecer la ruta al primer directorio
dir = "/content/kaggle/train/0"

# Recorrer cada elemento en el directorio
for path in os.listdir(dir):
    # Comprobar si el elemento actual es un archivo
    if os.path.isfile(os.path.join(dir, path)):
        # Si es un archivo, aumentar el contador de imágenes en 1
        initial_count += 1

# Establecer la ruta al segundo directorio
dir = "/content/kaggle/train/1"

# Recorrer cada elemento en el segundo directorio
for path in os.listdir(dir):
    # Comprobar si el elemento actual es un archivo
    if os.path.isfile(os.path.join(dir, path)):
        # Si es un archivo, aumentar el contador de imágenes en 1
        initial_count += 1

# Imprimir el número total de imágenes en ambos directorios
print(initial_count)


# Comprobamos que se han descargado todas las imágenes.

# In[ ]:


#cantidad de pacientes
len(train['patient_id'].unique())


# In[ ]:


# Seleccionar imágenes sin cáncer y almacenarlas en la variable "cancer_0"
cancer_0 = train.query('cancer == 0') 

# Seleccionar imágenes con cáncer y almacenarlas en la variable "cancer_1"
cancer_1 = train.query('cancer == 1') 

# Imprimir la cantidad de imágenes sin cáncer y el porcentaje de imágenes sin cáncer respecto al total de imágenes
print(f'Cantidad de imágenes que no presentan cáncer: {len(cancer_0)}')
print(f'Porcentaje de imágenes que no presentan cáncer: {len(cancer_0)/len(train)}%')

# Imprimir la cantidad de imágenes con cáncer y el porcentaje de imágenes con cáncer respecto al total de imágenes
print(f'Cantidad de imágenes que presentan cáncer: {len(cancer_1)}')
print(f'Porcentaje de imágenes que no presentan cáncer: {len(cancer_1)/len(train)}%')


# In[ ]:


# Obtener los pacientes con imágenes etiquetadas como sin cáncer (cancer = 0) y almacenarlos en la variable "patient_0"
patient_0 = cancer_0['patient_id'].unique()

# Obtener los pacientes con imágenes etiquetadas como con cáncer (cancer = 1) y almacenarlos en la variable "patient_1"
patient_1 = cancer_1['patient_id'].unique()

# Obtener los pacientes que tienen imágenes etiquetadas como sin cáncer y con cáncer y almacenarlos en la variable "inter"
inter = np.intersect1d(patient_0,patient_1)

# Imprimir la cantidad de pacientes que tienen imágenes etiquetadas como sin cáncer y con cáncer
print(inter)
print(f'\n Hay {len(inter)} pacientes que presentan imágenes de ambas categorias')


# In[ ]:


# Observar cuantas imagenes existen por cada paciente
train.query('patient_id == 106')


# In[ ]:


# Crear una tabla pivot que agrupa los pacientes por lateralidad y estado de cáncer
pivot1 = train.pivot_table(
    columns="cancer", # Columnas: estado de cáncer (0 o 1)
    index="laterality", # Índices: lateralidad (izquierda o derecha)
    values="patient_id", # Valores: número de pacientes
    aggfunc="count" # Función de agregación: contar número de pacientes
)

# Imprimir la tabla pivot
pivot1


# In[ ]:


# Crear un nuevo DataFrame con pacientes que tienen imágenes con ambas etiquetas de cáncer
df_inter = train.loc[train['patient_id'].isin(inter)]

# Crear una tabla pivot que agrupa las imágenes por paciente, lateralidad y estado de cáncer
pivot2 = df_inter.pivot_table(
    columns="cancer", # Columnas: estado de cáncer (0 o 1)
    index=["patient_id","laterality"], # Índices: paciente y lateralidad
    values="image_id", # Valores: número de imágenes
    aggfunc="count", # Función de agregación: contar número de imágenes
    fill_value = 0 # Reemplazar valores faltantes con 0
)

# Imprimir la tabla pivot
pivot2


# Los datos de entrenamiento están compuestos por $54.706$ imágenes en formato `.png` de tamaño $256\times256\times3$, correspondientes a $11.913$ pacientes.
# 
# Casi el $98\%$ de las imágenes corresponden a mamografías de pacientes que tienen cáncer. El datasets está muy desbalanceado.
# 
# Hay $480$ pacientes que tienen algunas imágenes categorizadas como **cancer = 0** y otras con **cancer = 1**. Esto puede deberse a que hay pacientes que presentan el cancer de mamas en una sola mama.
# 
# En la mayoría de los casos se cuenta con cuatro imágenes de cada paciente, que corresponden a las vistas **craniocaudal derecha** (view = CC - laterality = R), **craniocaudal izquierda** (view = CC - laterality = L), **mediolateral oblique derecha** (view = MLO - laterality = R) y **mediolateral oblique izquierda** (view = MLO - laterality = L).

# In[ ]:


def show_img(cancer:int,patient:int,image:list):
  '''cancer = 0 o 1
  patient = patien_id
  image = lista de image_id en el orden MLO izquierda, MLO derecha,
  CC izquierda, CC derecha'''

  path = "/content/kaggle/train/"

  # Cargamos las imágenes
  img1 = cv2.imread(path + str(cancer) + '/' + str(patient) + '_' + str(image[0]) + '.png')
  img2 = cv2.imread(path + str(cancer) + '/' + str(patient) + '_' + str(image[1]) + '.png')
  img3 = cv2.imread(path + str(cancer) + '/' + str(patient) + '_' + str(image[2]) + '.png')
  img4 = cv2.imread(path + str(cancer) + '/' + str(patient) + '_' + str(image[3]) + '.png')
  
  # Convertimos las imágenes a RGB
  img1_rgb = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
  img2_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
  img3_rgb = cv2.cvtColor(img3, cv2.COLOR_BGR2RGB)
  img4_rgb = cv2.cvtColor(img4, cv2.COLOR_BGR2RGB)

  # Mostramos información del paciente y las imágenes
  print(f'Patient_id = {patient} -- Cancer = {cancer}')
  print(70*'=')
  print('Mediolateral oblique izquierda \t \t Mediolateral oblique derecha')
  print(f'{img1.shape} \t \t \t \t {img2.shape} ')
  comp1 = np.hstack((img1, img2))  
  cv2_imshow(comp1)
  print('Craniocaudal izquierda \t \t \t Craniocaudal derecha')
  print(f'{img3.shape} \t \t \t \t {img4.shape} ')
  comp2 = np.hstack((img3, img4))
  cv2_imshow(comp2)


# A continuación mostramos las cuatro imágenes correspondientes a dos pacientes, uno cuyo diagnostico es negativo y uno cuyo diagnóstico es positivo.

# In[ ]:


train.query('patient_id == 10006')


# In[ ]:


show_img(0,10006,[1459541791,1864590858,462822612,1874946579])


# In[ ]:


train.query('patient_id == 1759')


# In[ ]:


show_img(1,1759,[1811195939,1005049159,1211304263,276588619])


# Histograma para mostrar el número de imágenes por paciente

# In[ ]:


images_counter = train["patient_id"].value_counts().sort_index()
fig = px.histogram(images_counter, text_auto=True, title="Número de imágenes por paciente")
fig.update_layout(bargap=0.2)
fig.show()


# ## Features age y cancer

# In[ ]:


# Graficamos la cantidad de pacientes con y sin cáncer según su edad
fig, ax1 = plt.subplots()

color = 'magenta' # Color para la barra de "cancer = 0"
ax1.set_xlabel('age') # Etiqueta del eje X
ax1.set_ylabel('cancer=0 cantidad', color=color) # Etiqueta del eje Y para "cancer = 0"
ax1.hist(train.loc[train['cancer'] == 0, 'age'].dropna(), bins=10, alpha=1, label='0', color=color)
ax1.tick_params(axis='y', labelcolor=color) # Configurando el color de la etiqueta del eje Y para "cancer = 0"

ax2 = ax1.twinx()  # Instanciamos un segundo eje que comparte el mismo eje x

color = 'yellowgreen' # Color para la barra de "cancer = 1"
ax2.set_ylabel('cancer=1 cantidad', color=color) # Etiqueta del eje Y para "cancer = 1"
ax2.hist(train.loc[train['cancer'] == 1, 'age'].dropna(), bins=10, alpha=0.8, label='1', color=color) # Graficando la frecuencia de "cancer = 1"
ax2.tick_params(axis='y', labelcolor=color) # Configurando el color de la etiqueta del eje Y para "cancer = 1"

fig.tight_layout()  # Ajustamos el layout para evitar que la etiqueta del eje y derecha esté recortada
plt.show() # Mostrar la gráfica


# In[ ]:


# Seleccionamos la columna 'age' del dataframe 'train'
data = train['age']

# Creamos un histograma con los datos de la columna 'age'
plt.hist(data, bins=10, color='magenta')

# Agregamos etiqueta al eje X
plt.xlabel("Age")

# Agregamos etiqueta al eje Y
plt.ylabel("Cantidad de pacientes")

# Mostramos el histograma
plt.show()


# In[ ]:


#agrupamos por paciente con cancer=0 y seleccionamos su edad
age_0 = cancer_0.groupby('patient_id')['age'].max().to_frame()

#agrupamos por paciente con cancer=1 y seleccionamos su edad
age_1 = cancer_1.groupby('patient_id')['age'].max().to_frame()


# In[ ]:


#Información estadística para 'cancer = 0' y 'age'
age_0['age'].describe()


# In[ ]:


#Información estadística para 'cancer = 1' y 'age'
age_1['age'].describe()


# Conclusiones:
# 
# * La feature **age**, para cada diagnóstico **cancer = 0** y **cancer = 1**, tiene una distribución normal.
# 
# * El paciente con cáncer de mamas de menor edad es de 38 años y el de más edad es de 89 años.
# 
# * Si bien el paciente de menor edad es de 38 años, el $75\%$ de los pacientes de mayor edad con cancer de mamas de este dataset, es mayor a 56 años.
# 
# * Hay un $50\%$ de pacientes con cancer cuyas edades van desde los 56 años a los 71 años.
# 
# 
# 
# 

# ## Features cancer y laterality

# In[ ]:


# Graficamos la cantidad de pacientes segun la lateralidad de la biopsia y si 
#tienen cancer o no utilizando el metodo countplot de seaborn
sns.countplot(x='laterality', hue='cancer', data=train)

# Agregamos una leyenda para la variable 'cancer' en la esquina superior derecha
plt.legend(loc='upper right', title='cancer')

# Mostramos el gráfico
plt.show()


# Según la lateralidad los datos están balanceados.

# ## Features cancer y view

# Al analizar la feature **view** observamos que hay otros valores además de los dos esperados (MLO y CC), pero las imágenes correspondientes a estas son muy pocas. Estas vista son complementarias:
# 
# * ML: vista mediolateral.
# 
# * LM: vista lateromedial.
# 
# * AT: Vista auxiliar (revisar esta info).
# 
# * LMO: Vista lateromedial oblicua.

# In[ ]:


train['view'].unique()


# In[ ]:


train.groupby('view')['image_id'].count()


# In[ ]:


train[train['view']=='AT']


# In[ ]:


#Gráfico de barras que muestra la distribución de las imágenes mamográficas 
#en el conjunto de datos train según su estado de cáncer y su "view" (vista).
sns.countplot(x='view', hue='cancer', data=train)
plt.legend(loc='upper right', title='cancer')
plt.show()


# ## Features view y laterality

# In[ ]:


# Este codigo crea una figura de 6 subplots (un gráfico por cada una de las 6 vistas)
# Cada subplot muestra la cantidad de imágenes por lateralidad en una determinada vista
# El eje Y muestra la cantidad de imágenes y el eje X muestra la lateralidad
# En cada subplot se utiliza un gráfico de barras para representar la cantidad de imágenes por lateralidad

# Creación de la figura y los subplots
views = list(train['view'].unique())
fig, axes = plt.subplots(nrows=1, ncols=6, figsize=(20,10))

# Iteración sobre cada vista
for i in range(len(views)):
    view = views[i]
    
    # Seleccionar solo las filas correspondientes a la vista actual
    temp = train[train['view'] == view]
    
    # Contar la cantidad de imágenes por lateralidad y guardar en un DataFrame
    temp = temp.groupby('laterality')['image_id'].count().to_frame()
    temp.reset_index(inplace=True)
    temp.columns = [view, 'image_count']
    
    # Creación del gráfico de barras en el subplot actual
    sns.barplot(data=temp, x=view, y = 'image_count', ax=axes[i])
    
    # Configuración del eje x
    plt.xlabel(view)

# Mostrar la figura
plt.show()


# Conclusiones:
# 
# * Parece que no hay una diferencia significativa entre **cancer = 1** y **cancer = 0**.
# 
# * Las vistas de **CC** y **MLO** son las más populares.

# ## Features cancer e implant

# Grafico de barras para la cantidad de pacientes con 'cancer' según la presencia o no de un 'implant'

# In[ ]:


# Esta línea utiliza la función countplot de seaborn para crear un gráfico de barras que cuenta la cantidad de casos de cáncer según haya o no implante
sns.countplot(x='implant', hue='cancer', data=train)
# Esta línea coloca la leyenda en la parte superior derecha del gráfico y le da un título de "cancer"
plt.legend(loc='upper right', title='cancer')
# Mostrar la figura
plt.show()


# ## Machine Ids

# Se cuentan el número de máquinas únicas (no se repiten) en la columna "machine_id"

# In[ ]:


train.machine_id.nunique()


# Se muestran en un gráfico de barras  la cantidad de mamografías realizadas en cada máquina para visualizar su distribución

# In[ ]:


fig, ax = plt.subplots(1,1,figsize=(15,5)) # Creación de una figura y un eje con tamaño (15,5)
# Creación del gráfico de barras con los valores de la columna "machine_id" del conjunto de datos "train"
sns.countplot(x=train.machine_id, palette='tab10', ax=ax) 
plt.show() # Mostrar el gráfico 


# Las mamografías fueron tomadas utilizando 10 dipositivos distintos, pero la gran mayoría fueron tomadas utilizando cuatro dispositivos (21, 29, 48 y 49).

# A continuación se mostrarar ejemplos de mamografías tomadas en los 5 dispositivos principales

# Machine ID 21

# In[ ]:


train.query('machine_id==21').head()


# In[ ]:


show_img(0,10011,[270344397,1031443799,220375232,541722628])


# Machine ID 29

# In[ ]:


train.query('machine_id==29').head(10)


# In[ ]:


show_img(0,10025,[1365269360,893612858,562340703,288394860])


# Machine ID 48

# In[ ]:


train.query('machine_id==48').head()


# In[ ]:


show_img(0,10124,[1891054212,473162373,2029770528,1919498169])


# Machine ID 49

# In[ ]:


train.query('machine_id==49').head(7)


# In[ ]:


show_img(0,10049,[906829939,94335194,349510516,1351270472])


# Machine ID 216

# In[ ]:


train.query('machine_id==216').head()


# In[ ]:


show_img(0,10038,[1967300488,850559196,2142944869,1350492010])


# El tamaño de las imágenes es siempre el mismo $256\times256\times3$ (no depende del dispositivo que tomó la tomografía) pero pareciera que el fondo si depende del dispositivo que se utilizó.

# ## Asociación entre features con chi2 y Cramer

# Utilizamos el estadístico chi-cuadrado y el p-valor para la prueba de hipótesis de independencia de las frecuencias observadas en la tabla de contingencia.
# 
# **H0 : (hipótesis nula) Las dos variables son independientes.**
# 
# **H1 : (hipótesis alternativa) Las dos variables no son independientes.**
# 
# Si el p-valor es mayor a 0.05 no rechazamos la hipótesis nula, es decir no tenemos evidencia suficiente para decir que existe una asociación entre las features. Si el p-valor es menor a 0.05, significa que existe una probabilidad menor a 0,05 de obtener frecuencias como las observadas en caso de ser H0 verdadera; en consecuencia, se rechaza H0 en favor de H1, apoyando la asociación entre las features.
# 
# Luego analizamos el grado de asociación utilizando el coeficiente de correlación de Cramer.
# 
# - correlación = 0: las variables no están asociadas.
# 
# - 0 < correlación < 0.25: **correlación débil**.
# 
# - 0.25 < correlación < 0.75: **correlación moderada**.
# 
# - correlación > 0.75: **correlación alta**.

# In[ ]:


# Observamos las columnas del DataFrame "train"
train.columns


# Función que realiza un test de chi-cuadrado entre dos variables y muestra los resultados en forma de estadístico, p-valor, grados de libertad y frecuencias esperadas.

# In[ ]:


def chi2(data, feature1:str, feature2:str):
  '''
  data = DataFrame
  feature1 y feature 2 = strings

  Realiza test chi2 e imprime:
  - estadistico
  - p-valor
  - gardo de libertad
  - Frecuencias esperadas

  H0 : (hipótesis nula) Las dos variables son independientes.
  H1 : (hipótesis alternativa) Las dos variables no son independientes.
  '''
  # Creación de la tabla de contingencia a partir de las dos variables
  table_contingencia = pd.crosstab(data[feature1],data[feature2])

  # Realización del test chi2 y almacenamiento de los resultados
  analisis = chi2_contingency(table_contingencia, correction=False)

  # Impresión de los resultados
  print(f'chi2: {analisis[0]}')
  print(f'p-value: {analisis[1]}')
  print(f'Degrees of freedom: {analisis[2]}')
  print(f'frequencies expected:\n {analisis[3]}')

  # Conclusión basada en el p-valor obtenido
  if analisis[1] < 0.05:
    print('\nLas dos features no son independientes')
  else:
    print('\nNo existe evidencia de asociación entre ambas features')


# El siguiente código define una función llamada asociacion_cramer que calcula el coeficiente de correlación de Cramér entre dos variables categóricas.
# 
# Los argumentos que se le pasan a la función son:
# 
# - data: un DataFrame que contiene los datos
# - feature1 y feature2: dos strings que representan las columnas que queremos comparar.
# 
# La función devuelve un número real entre 0 y 1 que representa la correlación entre ambas variables.

# In[ ]:


def asociacion_cramer(data, feature1:str, feature2:str):
    '''
    data = DataFrame
    feature1 y feature 2 = strings

    Devuelve el coeficinete de correlación de cramer (un valor entre 0 y 1):
    - valor = 0: las variables no están asociadas
    - 0 < valor < 0.25 --> asociación débil
    - 0.25 < valor < 0.75 --> asociación moderada
    - correlación > 0.75 --> correlación alta
    '''
    
    # Crea la tabla de contingencia de los valores de las features
    table_contingencia = np.array(pd.crosstab(data[feature1],data[feature2]))
    
    # Realiza el test chi2
    X2 = chi2_contingency(table_contingencia)[0]
    
    # Obtiene la suma total de la tabla de contingencia
    N = np.sum(table_contingencia)
    
    # Obtiene el tamaño de la dimension minima de la tabla de contingencia
    minimum_dimension = min(table_contingencia.shape)-1
    
    # Devuelve el coeficiente de correlación de cramertc
    return round(np.sqrt((X2/N) / minimum_dimension),3)


# ### Laterality y Cancer

# Realiza una prueba chi2 y una medición de asociación de Cramer para determinar  si hay una relación entre 'laterality' y 'cancer' en el conjunto de datos 'train'
# 

# In[ ]:


# Cálculo del test de chi-cuadrado
chi2(train,'laterality','cancer')


# In[ ]:


# Cálculo de asociación de Cramer
asociacion_cramer(train,'laterality','cancer')


# ### View y Cancer

# Realiza una prueba chi2 y una medición de asociación de Cramer para determinar si hay una relación entre 'View' y 'cancer' en el conjunto de datos 'train'

# In[ ]:


# Cálculo del test de chi-cuadrado
chi2(train,'view','cancer')


# In[ ]:


# Cálculo de asociación de Cramer
asociacion_cramer(train,'view','cancer')


# ### Implant y Cancer

# Realiza una prueba chi2 y una medición de asociación de Cramer para determinar si hay una relación entre 'Implant' y 'cancer' en el conjunto de datos 'train'

# In[ ]:


# Cálculo del test de chi-cuadrado
chi2(train,'implant','cancer')


# In[ ]:


# Cálculo de asociación de Cramer
asociacion_cramer(train,'implant','cancer')


# ### Machine_id y Cancer
# 
# 

# Realiza una prueba chi2 y una medición de asociación de Cramer para determinar si hay una relación entre 'Machine_id' y 'cancer' en el conjunto de datos 'train'

# In[ ]:


# Cálculo del test de chi-cuadrado
chi2(train,'machine_id','cancer')


# In[ ]:


# Cálculo de asociación de Cramer
asociacion_cramer(train,'machine_id','cancer')


# ### Edad y Cancer

# Realiza una prueba chi2 y una medición de asociación de Cramer para determinar si hay una relación entre 'age' y 'cancer' en el conjunto de datos 'train'

# In[ ]:


# Cálculo del test de chi-cuadrado
chi2(train,'age','cancer')


# In[ ]:


# Cálculo de asociación de Cramer
asociacion_cramer(train,'age','cancer')


# ### Conclusiones
# 
# No existe evidencia de asociación entre los siguientes pares de features:
# 
# - laterality y cancer.
# - view y cancer.
# 
# Existe evidencia de asociación entre los siguientes pares de features, pero el grado de asociación es muy débil según el coeficiente de asociación de Cramer:
# 
# - implant y cancer.
# - machine_id y cancer.
# - Edad y cancer.
