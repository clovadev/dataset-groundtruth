import argparse
import os

import torch
import torch.utils.data
import torchvision
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', type=str, default='../../data/voc', help='Path to voc dataset')
parser.add_argument('--dataset_download', type=bool, default=False, help='Whether to download the dataset.')
parser.add_argument("--save_folder", type=str, default='../../data/voc_grundtruth', help='Path to saving results')
args = parser.parse_args()
print(args)

# 데이터셋, 데이터로더 설정
dataset = torchvision.datasets.VOCDetection(root=args.dataset,
                                            year='2007',
                                            image_set='test',
                                            download=args.dataset_download,
                                            transform=torchvision.transforms.ToTensor())
dataloader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0)

# 클래스 정의와 인덱스 생성
classes = {}
class_names = ["aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
for i, name in enumerate(class_names):
    classes[name] = i

# bounding box colormap 설정
cmap = np.array(plt.cm.get_cmap('Paired').colors)
cmap_rgb: list = np.multiply(cmap, 255).astype(np.int32).tolist()

# groundtruth를 이미지로 저장하는 코드
os.makedirs(args.save_folder, exist_ok=True)
for _, target in tqdm.tqdm(dataloader, desc='Saving images'):
    # 현재 파일의 이름과 경로를 생성
    filename: str = target['annotation']['filename'][0]
    image_folder = os.path.join(args.dataset, 'VOCdevkit/VOC2007/JPEGImages')
    image_path = os.path.join(image_folder, filename)

    # 원본 이미지 열기
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    for object in target['annotation']['object']:
        # 객체의 클래스 번호와 bounding box의 좌표를 가져오기
        class_num = classes[object['name'][0]]
        x1, y1, x2, y2 = object['bndbox'].values()
        x1 = int(x1[0])
        y1 = int(y1[0])
        x2 = int(x2[0])
        y2 = int(y2[0])

        # bounding box color 설정
        color = tuple(cmap_rgb[class_num % len(cmap_rgb)])

        # bounding box 그리기
        draw.rectangle(((x1, y1), (x2, y2)), outline=color, width=2)

        # label 그리기
        text = object['name'][0]
        font = ImageFont.truetype('calibri.ttf', size=12)
        text_width, text_height = font.getsize(text)
        draw.rectangle(((x1, y1), (x1 + text_width, y1 + text_height)), fill=color)
        draw.text((x1, y1), text, fill=(0, 0, 0), font=font)

    # groundtruth 이미지 저장
    image.save(os.path.join(args.save_folder, filename))
    image.close()
