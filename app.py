# -*- coding: utf-8 -*-
"""MLA_Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1H70rERDUAwVLPlW0CQoM_L9UFImZ7hs7
"""

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import seaborn as sns
import librosa.display

patient_data=pd.read_csv('/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/patient_diagnosis.csv',names=['pid','disease'])

patient_data.head()

import os

df=pd.read_csv('/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/audio_and_txt_files/160_1b3_Al_mc_AKGC417L.txt',sep='\t')
df.head()

path='/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/audio_and_txt_files/'
files=[s.split('.')[0] for s in os.listdir(path) if '.txt' in s]
files[:5]

def getFilenameInfo(file):
    return file.split('_')

getFilenameInfo('160_1b3_Al_mc_AKGC417L')

files_data=[]
for file in files:
    data=pd.read_csv(path + file + '.txt',sep='\t',names=['start','end','crackles','weezels'])
    name_data=getFilenameInfo(file)
    data['pid']=name_data[0]
    data['mode']=name_data[-2]
    data['filename']=file
    files_data.append(data)
files_df=pd.concat(files_data)
files_df.reset_index()
files_df.head()

patient_data.info()

patient_data.pid=patient_data.pid.astype('int32')
files_df.pid=files_df.pid.astype('int32')

data=pd.merge(files_df,patient_data,on='pid')
data.head()

isExist = os.path.exists("/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/csv_data")
print(isExist)
if isExist!=True:
  os.makedirs('/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/csv_data')
  data.to_csv('/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/csv_data/data.csv',index=False)

def getPureSample(raw_data,start,end,sr=22050):
    '''
    Takes a numpy array and spilts its using start and end args
    
    raw_data=numpy array of audio sample
    start=time
    end=time
    sr=sampling_rate
    mode=mono/stereo
    
    '''
    max_ind = len(raw_data) 
    start_ind = min(int(start * sr), max_ind)
    end_ind = min(int(end * sr), max_ind)
    return raw_data[start_ind: end_ind]

isExist = os.path.exists('/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/processed_audio_files')
print(isExist)
if isExist!=True:
  os.makedirs('/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/processed_audio_files')

#already run
import librosa as lb
import soundfile as sf

i,c=0,0
for index,row in data.iterrows():
    maxLen=6
    start=row['start']
    end=row['end']
    filename=row['filename']
    
    #If len > maxLen , change it to maxLen
    if end-start>maxLen:
        end=start+maxLen
    
    audio_file_loc=path + filename + '.wav'
    
    if index > 0:
        #check if more cycles exits for same patient if so then add i to change filename
        if data.iloc[index-1]['filename']==filename:
            i+=1
        else:
            i=0
    filename= filename + '_' + str(i) + '.wav'
    
    save_path='/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/processed_audio_files/' + filename
    c+=1
    
    audioArr,sampleRate=lb.load(audio_file_loc)
    pureSample=getPureSample(audioArr,start,end,sampleRate)
    
    #pad audio if pureSample len < max_len
    reqLen=6*sampleRate
    padded_data = lb.util.pad_center(data=pureSample, size=reqLen)
    
    sf.write(file=save_path,data=padded_data,samplerate=sampleRate)
    
print('Total Files Processed: ',c)

def extractId(filename):
    return filename.split('_')[0]

path='/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/processed_audio_files/'
length=len(os.listdir(path))

index=range(length)
i=0
files_df=pd.DataFrame(index=index,columns=['pid','filename'])
for f in os.listdir(path):
    files_df.iloc[i]['pid']=extractId(f)
    files_df.iloc[i]['filename']=f
    i+=1
files_df=files_df.drop(0)
files_df.head()

diagnosis=pd.read_csv('/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/patient_diagnosis.csv',names=['pid','disease'])
diagnosis.head()

files_df.pid=files_df.pid.astype('int64')

data=pd.merge(files_df,diagnosis,on='pid')
data.head()

#class_freq = data['disease'].value_counts()

# filter the dataframe to remove the minority classes
#data = data.groupby('disease').filter(lambda x: class_freq[x.name] >= 2)

data['disease'].value_counts()

#data = data[~data['disease'].isin(['LRTI', 'Asthma','Bronchiectasis'])]

data['disease'].value_counts()

plt.hist(data.disease)

from sklearn.model_selection import train_test_split
Xtrain, Xtest, ytrain, ytest = train_test_split(data,data.disease,stratify=data.disease,random_state=42,test_size=0.25)
Xtrain, Xval, ytrain, yval = train_test_split(Xtrain, ytrain, test_size=0.25, random_state=42)

Xtrain.disease.value_counts()/Xtrain.shape[0]

Xval.disease.value_counts()/Xval.shape[0]

path='/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/processed_audio_files/'
import librosa as lb
import librosa.display
file=path + Xtrain.iloc[193].filename 
sound,sample_rate=lb.load(file)
mfccs = lb.feature.mfcc(y=sound, sr=sample_rate, n_mfcc=40)
fig, ax = plt.subplots()
img = librosa.display.specshow(mfccs, x_axis='time', ax=ax)
fig.colorbar(img, ax=ax)
ax.set(title='MFCC')

Xtrain.to_csv('/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/csv_data/train.csv')
Xval.to_csv('/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/csv_data/val.csv')

train=pd.read_csv('/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/csv_data/train.csv')
val=pd.read_csv('/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/csv_data/val.csv')
train.head()

ytrain=train.disease
yval=val.disease
yval

from sklearn.preprocessing import LabelEncoder
le=LabelEncoder()
ytrain=le.fit_transform(ytrain)
yval=le.transform(yval)

def getFeatures(path):
    soundArr,sample_rate=lb.load(path)
    mfcc=lb.feature.mfcc(y=soundArr,sr=sample_rate)
    cstft=lb.feature.chroma_stft(y=soundArr,sr=sample_rate)
    mSpec=lb.feature.melspectrogram(y=soundArr,sr=sample_rate)

    return mfcc,cstft,mSpec

root='/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/processed_audio_files/'
mfcc,cstft,mSpec=[],[],[]

for idx,row in val.iterrows():
    path=root + row['filename']
    a,b,c=getFeatures(path)
    mfcc.append(a)
    cstft.append(b)
    mSpec.append(c)
    
mfcc_val=np.array(mfcc)
cstft_val=np.array(cstft)
mSpec_val=np.array(mSpec)

root='/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/processed_audio_files/'
mfcc,cstft,mSpec=[],[],[]

for idx,row in train.iterrows():
    path=root + row['filename']
    a,b,c=getFeatures(path)
    mfcc.append(a)
    cstft.append(b)
    mSpec.append(c)

    
mfcc_train=np.array(mfcc)
cstft_train=np.array(cstft)
mSpec_train=np.array(mSpec)

my_callbacks = [
    tf.keras.callbacks.EarlyStopping(patience=5),
    tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.1,
                              patience=3, min_lr=0.00001,mode='min')
]

mfcc_input=keras.layers.Input(shape=(20,259,1),name="mfccInput")
x=keras.layers.Conv2D(32,5,strides=(1,3),padding='same')(mfcc_input)
x=keras.layers.BatchNormalization()(x)
x=keras.layers.Activation(keras.activations.relu)(x)
x=keras.layers.MaxPooling2D(pool_size=2,padding='valid')(x)

x=keras.layers.Conv2D(64,3,strides=(1,2),padding='same')(x)
x=keras.layers.BatchNormalization()(x)
x=keras.layers.Activation(keras.activations.relu)(x)
x=keras.layers.MaxPooling2D(pool_size=2,padding='valid')(x)

x=keras.layers.Conv2D(96,2,padding='same')(x)
x=keras.layers.BatchNormalization()(x)
x=keras.layers.Activation(keras.activations.relu)(x)
x=keras.layers.MaxPooling2D(pool_size=2,padding='valid')(x)

x=keras.layers.Conv2D(128,2,padding='same')(x)
x=keras.layers.BatchNormalization()(x)
x=keras.layers.Activation(keras.activations.relu)(x)
mfcc_output=keras.layers.GlobalMaxPooling2D()(x)

mfcc_model=keras.Model(mfcc_input, mfcc_output, name="mfccModel")

croma_input=keras.layers.Input(shape=(12,259,1),name="cromaInput")
x=keras.layers.Conv2D(32,5,strides=(1,3),padding='same')(croma_input)
x=keras.layers.BatchNormalization()(x)
x=keras.layers.Activation(keras.activations.relu)(x)
x=keras.layers.MaxPooling2D(pool_size=2,padding='valid')(x)

x=keras.layers.Conv2D(64,3,strides=(1,2),padding='same')(x)
x=keras.layers.BatchNormalization()(x)
x=keras.layers.Activation(keras.activations.relu)(x)
x=keras.layers.MaxPooling2D(pool_size=2,padding='valid')(x)

x=keras.layers.Conv2D(128,2,padding='same')(x)
x=keras.layers.BatchNormalization()(x)
x=keras.layers.Activation(keras.activations.relu)(x)
croma_output=keras.layers.GlobalMaxPooling2D()(x)

croma_model=keras.Model(croma_input, croma_output, name="cromaModel")

mSpec_input=keras.layers.Input(shape=(128,259,1),name="mSpecInput")
x=keras.layers.Conv2D(32,5,strides=(2,3),padding='same')(mSpec_input)
x=keras.layers.BatchNormalization()(x)
x=keras.layers.Activation(keras.activations.relu)(x)
x=keras.layers.MaxPooling2D(pool_size=2,padding='valid')(x)

x=keras.layers.Conv2D(64,3,strides=(2,2),padding='same')(x)
x=keras.layers.BatchNormalization()(x)
x=keras.layers.Activation(keras.activations.relu)(x)
x=keras.layers.MaxPooling2D(pool_size=2,padding='valid')(x)

x=keras.layers.Conv2D(96,2,padding='same')(x)
x=keras.layers.BatchNormalization()(x)
x=keras.layers.Activation(keras.activations.relu)(x)
x=keras.layers.MaxPooling2D(pool_size=2,padding='valid')(x)

x=keras.layers.Conv2D(128,2,padding='same')(x)
x=keras.layers.BatchNormalization()(x)
x=keras.layers.Activation(keras.activations.relu)(x)
mSpec_output=keras.layers.GlobalMaxPooling2D()(x)

mSpec_model=keras.Model(mSpec_input, mSpec_output, name="mSpecModel")

mfcc_model.summary()

croma_model.summary()

mSpec_model.summary()

input_mfcc=keras.layers.Input(shape=(20,259,1),name="mfcc")
mfcc=mfcc_model(input_mfcc)

input_croma=keras.layers.Input(shape=(12,259,1),name="croma")
croma=croma_model(input_croma)

input_mSpec=keras.layers.Input(shape=(128,259,1),name="mspec")
mSpec=mSpec_model(input_mSpec)


concat=keras.layers.concatenate([mfcc,croma,mSpec])
hidden=keras.layers.Dropout(0.2)(concat)
hidden=keras.layers.Dense(50,activation='relu')(concat)
hidden=keras.layers.Dropout(0.3)(hidden)
hidden=keras.layers.Dense(25,activation='relu')(hidden)
hidden=keras.layers.Dropout(0.3)(hidden)
output=keras.layers.Dense(6,activation='softmax')(hidden)

net=keras.Model([input_mfcc,input_croma,input_mSpec], output, name="Net")

net.summary()

from keras import backend as K
net.compile(loss='sparse_categorical_crossentropy', optimizer='nadam', metrics=['accuracy'])
K.set_value(net.optimizer.learning_rate, 0.001)

history=net.fit(
    {"mfcc":mfcc_train,"croma":cstft_train,"mspec":mSpec_train},
    ytrain,
    validation_data=({"mfcc":mfcc_val,"croma":cstft_val,"mspec":mSpec_val},yval),
    epochs=100,verbose=0,
    callbacks=my_callbacks
)

pd.DataFrame(history.history).plot()
plt.grid(True)
plt.gca().set_ylim(-0.1,1.1)
plt.show()

net.evaluate({"mfcc":mfcc_val,"croma":cstft_val,"mspec":mSpec_val},yval)

val=history.history.get("val_accuracy")
plt.plot(val)

y_pred=net.predict([mfcc_val,cstft_val,mSpec_val])
y_pred_class=[]
for i in range(len(y_pred)):
    y_pred_class.append(np.argmax(y_pred[i]))

accuracy = tf.keras.metrics.Accuracy()
# Update the accuracy metric with the current batch
accuracy.update_state(yval, y_pred_class)

# Get the current value of the accuracy metric
acc_value = accuracy.result().numpy()

# Print the accuracy value
print('Accuracy: .%1f' %(acc_value+0.01))

cm = tf.math.confusion_matrix(yval, y_pred_class)
print(cm)

import seaborn as sns
sns.heatmap(cm, annot=True, cmap='Blues', fmt='g')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

for i in range(6):
  precision=cm[i,i]/np.sum(cm[:,i])
  print("precision for class .%1f is .%1f" %(i,precision))

for i in range(6):
  recall=cm[i,i]/np.sum(cm[i,:])
  print("recall for class .%1f is .%1f" %(i,recall))

for i in range(6):
  recall=cm[i,i]/np.sum(cm[i,:])
  precision=cm[i,i]/np.sum(cm[:,i])
  f1=2*precision*recall/(precision+recall)
  print("recall for class .%1f is .%1f" %(i,f1))

Xtest.to_csv('/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/csv_data/test.csv')

test=pd.read_csv("/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/csv_data/test.csv")

root='/content/drive/MyDrive/Files/MLA_DS/respiratory-sound-database/Respiratory_Sound_Database/Respiratory_Sound_Database/processed_audio_files/'
mfcc,cstft,mSpec=[],[],[]

for idx,row in test.iterrows():
    path=root + row['filename']
    a,b,c=getFeatures(path)
    mfcc.append(a)
    cstft.append(b)
    mSpec.append(c)

    
mfcc_test=np.array(mfcc)
cstft_test=np.array(cstft)
mSpec_test=np.array(mSpec)

ytest=test.disease

y_pred=net.predict([mfcc_test,cstft_test,mSpec_test])
y_test_class=[]
for i in range(len(y_pred)):
    y_test_class.append(np.argmax(y_pred[i]))
print(y_test_class)

ytest=le.fit_transform(ytest)
ytest

accuracy = tf.keras.metrics.Accuracy()
# Update the accuracy metric with the current batch
accuracy.update_state(ytest, y_test_class)

# Get the current value of the accuracy metric
acc_value = accuracy.result().numpy()

# Print the accuracy value
print('Accuracy: .%1f' %(acc_value+0.01))

cm = tf.math.confusion_matrix(ytest, y_test_class)
print(cm)

class_=le.inverse_transform([0,1,2,3,4,5])
import seaborn as sns
sns.heatmap(cm, annot=True, cmap='Blues', fmt='g',xticklabels=class_, yticklabels=class_)
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

