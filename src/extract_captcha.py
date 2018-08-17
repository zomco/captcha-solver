# coding: utf-8
import glob
import cv2
import os
import shutil
import imutils
import numpy as np
from .helpers import box_iou


def extract(generate_dir='tmp/generate', extract_dir='tmp/extract', total=10000, contour='all'):
    '''
    把打好标签的样本分割成单字符图像
    '''
    if not os.path.exists(generate_dir):
        return None
    images = glob.glob('{}/*.png'.format(generate_dir))
    if len(images) < total:
        total = len(images)

    # 检查输出路径
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
        os.makedirs(extract_dir)
    else:
        os.makedirs(extract_dir)
    
    counts = {}
    for (i, image) in enumerate(images[:total]):
        # 提取图片的验证码
        filename = os.path.basename(image)
        code = os.path.splitext(filename)[0]
        print("正在读取验证码 {} 图片 {}/{}".format(code, i + 1, len(images[:total])))
        # 读取图片，然后灰度化，边界扩展，平均模糊，二值化，查找轮廓
        im = cv2.imread(image)
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 7)
        # 将图片等分成数个区域，分别对区域内字符查找轮廓
        height, width = blur.shape
        length = len(code)
        average = int(width / length)
        for j, label in enumerate(code):
            area = blur[:,j*average:(j+1)*average]
            thresh = cv2.threshold(area, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            contours= cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
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
            # 将结果保存到目标文件夹
            x, y, w, h = region
            char_im = blur[y:y+h, x+j*average:x+w+j*average]
            char_dir = os.path.join('tmp/extract', label)
            if not os.path.exists(char_dir):
                os.makedirs(char_dir)
            count = counts.get(label, 1)
            char_name = "{}.png".format(str(count).zfill(6))
            cv2.imwrite(os.path.join(char_dir, char_name), char_im)
            print('{} 保存到 {}'.format(char_name, char_dir))
            counts[label] = count + 1
