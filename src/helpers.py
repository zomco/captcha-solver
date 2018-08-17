# coding: utf-8
import imutils
import cv2


def resize_to_fit(image, width, height):
    '''
    图像缩放到特定尺寸
    '''
    (h, w) = image.shape[:2]
    if w > h:
        image = imutils.resize(image, width=width)
    else:
        image = imutils.resize(image, height=height)

    padW = int((width - image.shape[1]) / 2.0)
    padH = int((height - image.shape[0]) / 2.0)
    image = cv2.copyMakeBorder(image, padH, padH, padW, padW, cv2.BORDER_REPLICATE)
    image = cv2.resize(image, (width, height))

    return image


def overlap(x1, w1, x2, w2):
    l1 = x1 - w1 / 2.
    l2 = x2 - w2 / 2.
    left = max(l1, l2)
    r1 = x1 + w1 / 2.
    r2 = x2 + w2 / 2.
    right = min(r1, r2)
    return right - left


def box_inter(box1, box2):
    w = overlap(box1.get('x'), box1.get('w'), box2.get('x'), box2.get('w'))
    h = overlap(box1.get('y'), box1.get('h'), box2.get('y'), box2.get('h'))
    if w < 0 or h < 0:
        return 0
    area = w * h
    return area


def box_union(box1, box2):
    i = box_inter(box1, box2)
    u = box1.get('w') * box1.get('h') + box2.get('w') * box2.get('h') - i
    return u


def box_iou(box1, box2):
    return box_inter(box1, box2) / box_union(box1, box2)
