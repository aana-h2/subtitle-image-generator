import re
import sys

from moviepy.editor import VideoFileClip
from PIL import Image
from typing import List, Tuple
import numpy as np
from numpy import array
from argparse import ArgumentParser


# limits coordinate is different from PIL, its (0,0) in left bottom.
def cal_area(img_w: int, img_h: int, limits: List[int]) -> Tuple[int, int, int, int]:
    """
    For convenience, coordinate is different from PIL

        |
        |
        |------------
    (0,0)
    """
    xs = limits[0]
    xe = limits[1]
    ys = limits[2]
    ye = limits[3]

    def get_default(flag, v, default_v):
        return default_v if flag == -1 else v

    return (
        get_default(xs, xs, 0),
        get_default(ye, img_h - ye, 0),
        get_default(xe, xe, img_w),
        get_default(ys, img_h - ys, img_h),
    )


# 按条裁剪。宽度等于图片宽度，高度等于目标高度。
def crop_in_row(image_list: List[array], limits: List[int], full_frame_list: List[int]) -> List[Image.Image]:
    """
    (0,0) ______________
         |
         |
         |
         |
         |
    """
    cropped_list = []

    if len(image_list) == 0:
        return []

    # TODO -- crop it in numpy array may more faster?
    w = np.size(image_list[0], 1)
    h = np.size(image_list[0], 0)
    area = cal_area(w, h, limits)

    for idx, image_arr in enumerate(image_list):
        image = Image.fromarray(image_arr)
        if idx in full_frame_list:
            cropped_image = image
        else:
            cropped_image = image.crop(area)
        cropped_list.append(cropped_image)
    return cropped_list


# 从上到下进行拼接。
# 创建一个空白的图，其长度为所有的片段的和，宽度为所有片段的max。
# 图的底色为黑色。
def merge_rows(image_list: List[Image.Image]) -> Image.Image:
    total_height = 0
    max_width = 0
    for image in image_list:
        w, h = image.size
        max_width = max(max_width, w)
        total_height += h
    background = Image.new('RGB', (max_width, total_height))
    paste_x = 0
    paste_y = 0
    for image in image_list:
        background.paste(image, (paste_x, paste_y))
        paste_y += image.height
    return background


def read_file_time_list(filename: str) -> List[str]:
    assert False


def cli():
    arg_parser = ArgumentParser(description="A tool for creating subtitle compound image from video.")
    arg_parser.add_argument('-t', type=str, help='Time Point List', nargs='+', action='append')
    arg_parser.add_argument('-f', type=str, help='Time Point File', nargs=1)
    arg_parser.add_argument('-o', type=str, help='Output Image File', nargs=1, default='compound_image.jpg')
    arg_parser.add_argument('filename', type=str, help='File Name For Video', metavar='video file name')
    arg_parser.add_argument('-xs', type=int, nargs=1, help='X start', default=[-1])
    arg_parser.add_argument('-xe', type=int, nargs=1, help='X end', default=[-1])
    arg_parser.add_argument('-ys', type=int, nargs=1, help='T start', default=[-1])
    arg_parser.add_argument('-ye', type=int, nargs=1, help='Y end', default=[-1])

    arg_parser.add_argument('height', type=int, help='Single pic crop height', metavar='crop height')
    args_ns = arg_parser.parse_args()

    if args_ns.t:
        full_frame_ids = []
        tl = []
        for i, tp in enumerate(args_ns.t[0]):
            # will not support more control method, <full> is enough
            if re.search('<full>', tp):
                full_frame_ids.append(i)
                tl.append(tp.replace('<full>', '', -1))
            else:
                tl.append(tp)
    else:
        print("Must provide a time list, use --help to get usage guideline.", file=sys.stderr)
        return

    limits = []

    for p in ['xs', 'xe', 'ys', 'ye']:
        limits.append(args_ns.__dict__[p][0])

    video_name = args_ns.filename
    with VideoFileClip(video_name) as video:
        frame_list = [video.get_frame(t=t) for t in tl]

        merged_img = merge_rows(crop_in_row(frame_list, limits, full_frame_ids))
        output_file = args_ns.o[0]
        merged_img.save(output_file)


if __name__ == '__main__':
    cli()
