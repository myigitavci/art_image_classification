# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 10:02:21 2022

@author: yigitavcii
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.applications.efficientnet import EfficientNetB7

from tensorflow.keras.layers import Input
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.layers import GlobalAveragePooling2D

# this could also be the output a different Keras model or layer

import matplotlib
from matplotlib import pylab as plt
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers import SGD
import scipy.io as sio
import numpy as np

from imgaug import augmenters as iaa

import os
#%%
def preprocess_input(x):
    x /= 255.
    x -= 0.5
    x *= 2.
    return x
def preprocess_input_resnet(x):
    x /= 255.

    return x
def random_crop(img, random_crop_size):
    # Note: image_data_format is 'channel_last'
    assert img.shape[2] == 3
    height, width = img.shape[0], img.shape[1]
    dy, dx = random_crop_size
    x = np.random.randint(0, width - dx + 1)
    y = np.random.randint(0, height - dy + 1)
    return img[y:(y+dy), x:(x+dx), :]


def crop_generator(batches, crop_length):
    """Take as input a Keras ImageGen (Iterator) and generate random
    crops from the image batches generated by the original iterator.
    """
    while True:
        batch_x, batch_y = next(batches)
        batch_crops = np.zeros((batch_x.shape[0], crop_length, crop_length, 3))
        for i in range(batch_x.shape[0]):
            batch_crops[i] = random_crop(batch_x[i], (crop_length, crop_length))
        yield (batch_crops, batch_y)
#%%
# definitions
dpRoot = 'D:/ee58j_final_project'
os.chdir(dpRoot)
dptrain='D:/ee58j_final_project/art_imgs_10'
dpval='D:/ee58j_final_project/art_imgs_10'
dptest='D:/ee58j_final_project/test_set_10'

dpTest=dpRoot+'/test_set_10'
train_loss=[]
val_loss=[]
train_acc=[]
val_acc=[]
batch_size = 8
#image_size=(580,580)
#%%
# creating data generators and load the data
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img


preprocess_input=tf.keras.applications.inception_v3.preprocess_input
preprocess_input=tf.keras.applications.resnet50.preprocess_input
preprocess_input=tf.keras.applications.efficientnet.preprocess_input

train_datagen = ImageDataGenerator(
        #rescale=1./255,
        #validation_split=0.15,
        zoom_range=[0.5,1.0],
      preprocessing_function=preprocess_input,
        validation_split=0.2,

        fill_mode='nearest')

val_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    #rescale=1./255,
        zoom_range=[0.5,1.0],


    preprocessing_function=preprocess_input,

   validation_split=0.2
)          

test_datagen = ImageDataGenerator(        preprocessing_function=preprocess_input,
)

train_ds = train_datagen.flow_from_directory(
    dptrain,
    subset="training",
    shuffle=True,
    seed=1337,
    batch_size=batch_size,
)

val_ds = val_datagen.flow_from_directory(
    dpval,
    subset="validation",
    shuffle=True,
    seed=1337,
    batch_size=batch_size,
)
test_ds = test_datagen.flow_from_directory(
    dptest,
    seed=1337,
    batch_size=batch_size,
    shuffle=False
   
)

#%%
# choose the  model

base_model = ResNet50(
    weights='imagenet',  # Load weights pre-trained on ImageNet.
    input_shape=(256, 256, 3),
    include_top=False)  # Do not include the ImageNet classifier at the top.
  #%%
base_model = InceptionV3(
    weights='imagenet',  # Load weights pre-trained on ImageNet.
    input_shape=(256, 256, 3),
    include_top=False)  # Do not include the ImageNet classifier at the top.
#%%
base_model = EfficientNetB7(
    weights='imagenet',  # Load weights pre-trained on ImageNet.
    input_shape=(256, 256, 3),
    include_top=False)  # Do not include the ImageNet classifier at the top.


  #%%
# fine tuning part


image_batch, label_batch = next(iter(train_ds))
feature_batch = base_model(image_batch)  

global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
feature_batch_average = global_average_layer(feature_batch)
prediction_layer = tf.keras.layers.Dense(10)
prediction_batch = prediction_layer(feature_batch_average)


# make only the last layers trainable

base_model.trainable = False
inputs = keras.Input(shape=(256, 256, 3))
x = inputs
x = base_model(x, training=False)
x = global_average_layer(x)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = prediction_layer(x)
model = tf.keras.Model(inputs, outputs)
model.summary()
#%%
base_model.trainable = True
print("Number of layers in the base model: ", len(base_model.layers))
fine_tune_at =100

# Freeze all the layers before the `fine_tune_at` layer
for layer in base_model.layers[:fine_tune_at]:
  layer.trainable = False
model.summary()

#%%
base_learning_rate = 0.001
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=base_learning_rate/10),
              loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

#%%
history = model.fit_generator(train_ds,
                    epochs=10,
                    validation_data=val_ds
)
#%%
# look at the performance
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

acc=model.evaluate(x=test_ds)

#%%
# train more of the last layers 

base_model.trainable = True
print("Number of layers in the base model: ", len(base_model.layers))
fine_tune_at =200

# Freeze all the layers before the `fine_tune_at` layer
for layer in base_model.layers[:fine_tune_at]:
  layer.trainable = False
model.summary()

model.load_weights("art_classification_effnet_10.h5")
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=base_learning_rate),
              loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])
#%%
from keras.callbacks import EarlyStopping

early_stopping_monitor = EarlyStopping(
    monitor='val_accuracy',
    min_delta=0,
    patience=5,
    verbose=0,
    mode='auto',
    baseline=None,
    restore_best_weights=True
)
fine_tune_epochs = 5
total_epochs =  10 + fine_tune_epochs

history_fine= model.fit(train_ds,
                         epochs=total_epochs,
                         initial_epoch=history.epoch[-1],
                         callbacks=[early_stopping_monitor],
                         validation_data=val_ds)
#%%
# look performance again
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

acc=model.evaluate(x=test_ds)

#%%


# Plotting the confusion matrix
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
y_pred_ts=model.predict(test_ds)

s=np.argmax(y_pred_ts,axis=1)
cf_matrix=confusion_matrix(test_ds.classes, s)



def plot_confusion_matrix(cm,
                          target_names,
                          title='Confusion matrix',
                          cmap=None,
                          normalize=True):
   
    import matplotlib.pyplot as plt
    import numpy as np
    import itertools

    accuracy = np.trace(cm) / np.sum(cm).astype('float')
    misclass = 1 - accuracy
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    if cmap is None:
        cmap = plt.get_cmap('Blues')

    plt.figure(figsize=(12, 12))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()

    if target_names is not None:
        tick_marks = np.arange(len(target_names))
        plt.xticks(tick_marks, target_names, rotation=45)
        plt.yticks(tick_marks, target_names)




    thresh = cm.max() / 1.5 if normalize else cm.max() / 2
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        if normalize:
            plt.text(j, i, "{:0.2f}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")
        else:
            plt.text(j, i, "{:,}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")


    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label\naccuracy={:0.4f}; misclass={:0.4f}'.format(accuracy, misclass))
    plt.show()
 
    
plot_confusion_matrix(cm           = cf_matrix,                  # confusion matrix created by
                          target_names=["Buys, Jacobus","Fokke, Simon","Galle, Philips","Hogenberg, Frans","Hooghe, Romeyn de","Lodewijk XIV "," Manufaktur","Picart, Bernard","Rembrandt","Visscher, Claes Jansz. (II)"]  ,                              # sklearn.metrics.confusion_matrix
                          normalize    = True,                # show proportions
                          title        = 'Confusion matrix')
