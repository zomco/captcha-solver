# coding: utf-8
import cv2
import pickle
import os.path
import numpy as np
from imutils import paths
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.layers.core import Flatten, Dense
from .helpers import resize_to_fit


def train(extract_dir='tmp/extract', label_file='tmp/label.dat', model_file='tmp/model.hdf5'):
    char_ims = []
    labels = []
    for char in paths.list_images(extract_dir):
        # 读取字符图片，然后灰度化，调整大小，数据格式扩展成三纬
        char_im = cv2.imread(char)
        gray = cv2.cvtColor(char_im, cv2.COLOR_BGR2GRAY)
        resize = resize_to_fit(gray, 20, 20)
        expand = np.expand_dims(resize, axis=2)
        label = char.split(os.path.sep)[-2]
        char_ims.append(expand)
        labels.append(label)
    # 图片像素值归一化
    char_ims = np.array(char_ims, dtype="float") / 255.0
    labels = np.array(labels)
    # 构造训练集和测试集，标签二值化
    (x_train, x_test, y_train, y_test) = train_test_split(char_ims, labels, test_size=0.25, random_state=0)
    lb = LabelBinarizer().fit(y_train)
    y_train = lb.transform(y_train)
    y_test = lb.transform(y_test)
    with open(label_file, "wb") as f:
        pickle.dump(lb, f)
    # 定义网络模型
    model = Sequential()
    # 第一个卷积层
    model.add(Conv2D(32, (5, 5), padding="same", input_shape=(20, 20, 1), activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
    # 第二个卷积层
    model.add(Conv2D(64, (5, 5), padding="same", activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
    # 全连接层
    model.add(Flatten())
    model.add(Dense(500, activation="relu"))
    # 输出层
    model.add(Dense(34, activation="softmax"))
    # 构造模型并启动训练，将训练结果保存到
    model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
    model.fit(x_train, y_train, validation_data=(x_test, y_test), batch_size=32, epochs=10, verbose=1)
    model.save(model_file)
    model.summary()
