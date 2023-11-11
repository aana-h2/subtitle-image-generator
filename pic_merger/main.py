import sys

from moviepy.editor import VideoFileClip
from PIL import Image
from typing import List
from numpy import array
from argparse import ArgumentParser

# 按条裁剪。宽度等于图片宽度，高度等于目标高度。
def crop_in_row(height: int, image_list: List[Image.Image]) -> List[Image.Image]:
    """
    (0,0) ______________
         |
         |
         |
         |
         |
    """
    cropped_list = []
    for image in image_list:
        w, h = image.size
        crop_height = min(height, h)
        cropped_image = image.crop((0, h - crop_height, w, h))
        cropped_list.append(cropped_image)
    return cropped_list


def crop_in_row_numpy(height: int, array_list: List[array]) -> List[Image.Image]:
    image_list = [Image.fromarray(arr) for arr in array_list]

    return crop_in_row(height, image_list)


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
    """
    For convenience, coordinate is different from PIL

        |
        |
        |------------
    (0,0)
    """
    arg_parser = ArgumentParser(description="A tool for creating subtitle compound image from video.")

    arg_parser.add_argument('-t', type=str, help='Time Point List', nargs='+', action='append')
    arg_parser.add_argument('-f', type=str, help='Time Point File', nargs=1)
    arg_parser.add_argument('-o', type=str, help='Output Image File', nargs=1, default='compound_image.jpg')
    arg_parser.add_argument('filename', type=str, help='File Name For Video', metavar='video file name')
    arg_parser.add_argument('height', type=int, help='Single pic crop height', metavar='crop height')


    args_ns = arg_parser.parse_args()

    if args_ns.t:
        tl = args_ns.t[0]
    elif args_ns.f:
        tl = read_file_time_list(args_ns.f[0])
    else:
        print("Must provide a time list, use --help to get usage guideline.", file=sys.stderr)
        return

    video_name = args_ns.filename
    with VideoFileClip(video_name) as video:
        frame_list = [video.get_frame(t=t) for t in tl]
        merged_img = merge_rows(crop_in_row_numpy(100, frame_list))
        output_file = args_ns.o[0]
        merged_img.save(output_file)


if __name__ == '__main__':
    cli()
