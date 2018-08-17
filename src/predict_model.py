# coding: utf-8
from keras.models import load_model
from imutils import paths
import numpy as np
import imutils
import cv2
import os
import pickle
import shutil
from .helpers import box_iou, resize_to_fit


def predict(images=[], label_file='tmp/labels.dat', model_file='tmp/model.hdf5', predict_dir='tmp/predict', code_length=4, contour='all'):
    # 加载标签文件和模型文件
    with open(label_file, 'rb') as f:
        lb = pickle.load(f)
    model = load_model(model_file)

    # 检查输出路径
    if os.path.exists(predict_dir):
        shutil.rmtree(predict_dir)
        os.makedirs(predict_dir)
    else:
        os.makedirs(predict_dir)

    # 遍历图像文件识别验证码
    codes = []
    total = len(images)
    for i, image in enumerate(images):
        # 读取图片，然后灰度化，边界扩展，平均模糊，二值化，查找轮廓
        im = cv2.imread(image)
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 5)
        # 单通道转换为三通道，保存识别结果
        output = cv2.merge([blur] * 3)
        predictions = []
        # 将图片等分成数个区域，分别对区域内字符查找轮廓
        height, width = blur.shape
        average = int(width / code_length)
        for j in range(code_length):
            area = blur[:,j*average:(j+1)*average]
            thresh = cv2.threshold(area, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = contours[0] if imutils.is_cv2() else contours[1]
            # 根据轮廓分割图片
            region = (0, 0, average, height)
            if contour != 'all':
                for contour in contours:
                    (x, y, w, h) = cv2.boundingRect(contour)
                    # 跳过无效的区域
                    if h < 2 * height / 3 or w < average / 2:
                        continue
                    # 如果区域重叠，取面积较小的区域
                    x_, y_, w_, h_ = region
                    box1 = {'x': x, 'y': y, 'w': w, 'h': h}
                    box2 = {'x': x_, 'y': y_, 'w': w_, 'h': h_}
                    iou = box_iou(box1, box2)
                    if iou > 0.4 and w * h < w_ * h_:
                        region = (x, y, w, h)
            # 读取字符图片，调整大小，数据格式扩展成四纬
            x, y, w, h = region
            mx = x+j*average
            char_im = blur[y:y+h, mx:mx+w]
            resize = resize_to_fit(char_im, 20, 20)
            expand = np.expand_dims(resize, axis=2)
            expand = np.expand_dims(expand, axis=0)
            # 执行图片识别，从二值化的识别结果转化为标签
            prediction = model.predict(expand)
            letter = lb.inverse_transform(prediction)[0]
            predictions.append(letter)
            # 识别结果绘制到原图上
            cv2.rectangle(output, (mx, y), (mx + w, y + h), (0, 255, 0), 1)
            cv2.putText(output, letter, (mx, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

        # 打印识别结果
        code = ''.join(predictions)
        codes.append(code)
        # print("验证码是: {} {}/{}".format(code, i + 1, total))
        cv2.imwrite(os.path.join(predict_dir, '{}.png'.format(code)), output)
    return codes
