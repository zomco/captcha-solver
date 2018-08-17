# coding: utf-8
import random
import os
import shutil
from .image import ImageCaptcha
from .helpers import box_iou


def generate(generate_dir='tmp/generate', total=10000, code_length=4):
    '''
    自动生成样本
    '''
    image = ImageCaptcha(fonts=['eopt_fonts/tavern-new.ttf'], font_sizes=(120,))
    chars = list('2345678ABCDEFGHJKLMNPQRSTUVWXYZ')

    # 检查输出路径
    if os.path.exists(generate_dir):
        shutil.rmtree(generate_dir)
        os.makedirs(generate_dir)
    else:
        os.makedirs(generate_dir)

    for i in range(total):
        code = ''.join(random.choice(chars) for _ in range(code_length))
        image.write(code, '{}/{}.png'.format(generate_dir, code))
        print('{}.png 保存到 {} {}/{}'.format(code, generate_dir, i + 1, total))

