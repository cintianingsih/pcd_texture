from argparse import Namespace
import os
from typing import Tuple
import cv2

import numpy as np
import torch
import torchvision
import torchvision.transforms.functional as transforms
from PIL import Image
from torch import Tensor
from torch.nn.functional import interpolate


def load_styles(style_files, size, scale, oversize=False, device="cpu", memory_format=torch.contiguous_format):
    styles = []
    for style_file in style_files:
        styles.append(load_image(style_file, size, scale, not oversize, device=device, memory_format=memory_format))
    return styles


def maybe_load_content(content_file, size, device="cpu", memory_format=torch.contiguous_format):
    content = None
    if content_file is not None:
        content = load_image(content_file, size, oversize=False, device=device, memory_format=memory_format)
    return content


def load_image(path, size, scale=1, oversize=True, device="cpu", memory_format=torch.contiguous_format):
    img = Image.open(path).convert(mode="RGB")
    img = img.resize(get_size(size, scale, img.size[0], img.size[1], oversize), Image.LANCZOS)
    return transforms.to_tensor(img).unsqueeze(0).to(device, memory_format=memory_format)


def get_size(size: int, scale: float, h: int, w: int, oversize: bool = False):
    ssize = size * scale
    wpercent = ssize / float(h)
    hsize = int((float(w) * float(wpercent)))

    if oversize:
        size = min(int(ssize), h)
        hsize = min(hsize, w)

    return round32(size), round32(hsize)

def save_image(output: Tensor, args: Namespace):
    # Ganti bagian ini
    outname = "img_result"

    # Check if an image with the same name already exists
    existing_files = [f for f in os.listdir(args.output_dir) if f.startswith(outname)]
    for existing_file in existing_files:
        os.remove(os.path.join(args.output_dir, existing_file))

    for o, out in enumerate(output):
        torchvision.utils.save_image(
            out, f"{args.output_dir}/{outname}" + (f"_{o + 1}" if len(output) > 1 else "") + ".png"
        )



def get_iters_and_sizes(size: int, iters: int, passes: int, use_multires: bool):
    # more iterations for smaller sizes and deeper layers

    if use_multires:
        iters_per_pass = np.arange(2 * passes, passes, -1)
        iters_per_pass = iters_per_pass / np.sum(iters_per_pass) * iters

        sizes = np.linspace(256, size, passes)
        # round to nearest multiple of 32, so that even after 4 max pools the resolution is an even number
        sizes = (32 * np.round(sizes / 32)).astype(np.int32)
    else:
        iters_per_pass = np.ones(passes) * int(iters / passes)
        sizes = [size] * passes

    proportion_per_layer = np.array([64, 128, 256, 512, 512]) + 64
    proportion_per_layer = proportion_per_layer / np.sum(proportion_per_layer)
    iters = (iters_per_pass[:, None] * proportion_per_layer[None, :]).astype(np.int32)

    return iters.tolist(), sizes.tolist()


def name(filepath: str):
    return filepath.split("/")[-1].split(".")[0]


def round32(integer: int):
    return int(integer + 32 - 1) & -32


def to_nchw(x: Tensor):
    return x.permute(0, 3, 1, 2)


def to_nhwc(x: Tensor):
    return x.permute(0, 2, 3, 1)


def resize(x: Tensor, size: Tuple[int, int]):
    return interpolate(x, size=size, mode="bicubic", align_corners=False, antialias=True)

def brightness_multiplication():
    img = Image.open("output/img_result.png")
    img_arr = np.asarray(img)
    img_arr = img_arr*1.25
    img_arr = np.clip(img_arr, 0, 255)
    new_arr = img_arr.astype('uint8')
    new_img = Image.fromarray(new_arr)
    new_img.save("output/img_result.png")

def brightness_division():
    img = Image.open("output/img_result.png")
    img_arr = np.asarray(img)
    img_arr = img_arr/1.25
    img_arr = np.clip(img_arr, 0, 255)
    new_arr = img_arr.astype('uint8')
    new_img = Image.fromarray(new_arr)
    new_img.save("output/img_result.png")

def bandFilterPass():
    img = cv2.imread("output/img_result.png")
    # create the band pass filter
    bandFilter = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    # apply the band pass filter to the image
    bandFilterImage = cv2.filter2D(img,-1,bandFilter)
    cv2.imwrite("output/img_result.png", bandFilterImage)