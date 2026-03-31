#!/usr/bin/env python
# -*- coding: utf-8 -*-

# refer to `https://bitbucket.org/akorn/wheezy.captcha`

import math
import os.path
import random
import secrets
import string
from io import BytesIO

from PIL import Image, ImageFilter, ImageFont
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype, ImageFont

# 安全字符集：数字 + 大写字母（去除 0, O, 1, I, l 等易混淆字符）
SAFE_CHARS = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
DEFAULT_FONTS = ['../fonts/Arial.ttf', '../fonts/Georgia.ttf', '../fonts/actionj.ttf']


class Bezier:
    """贝塞尔曲线生成器"""
    def __init__(self):
        self.tsequence = tuple([t / 20.0 for t in range(21)])
        self.beziers = {}

    @staticmethod
    def pascal_row(n):
        result = [1]
        x, numerator = 1, n
        for denominator in range(1, n // 2 + 1):
            x *= numerator
            x /= denominator
            result.append(x)
            numerator -= 1
        if n & 1 == 0:
            result.extend(reversed(result[:-1]))
        else:
            result.extend(reversed(result))
        return result

    def make_bezier(self, n):
        try:
            return self.beziers[n]
        except KeyError:
            combinations = self.pascal_row(n - 1)
            result = []
            for t in self.tsequence:
                tpowers = (t ** i for i in range(n))
                upowers = ((1 - t) ** i for i in range(n - 1, -1, -1))
                coefs = [c * a * b for c, a, b in zip(combinations,
                                                      tpowers, upowers)]
                result.append(coefs)
            self.beziers[n] = result
            return result


class Captcha(object):
    def __init__(self):
        self.font_sizes = (90, 100, 110)
        self.squeeze_factor = 1.15
        self._bg_color = None
        self.height = None
        self.width = None
        self._color = self.random_color(0, 80)          # 深色文字
        self._text = None
        self.fonts = None
        self._bezier = Bezier()
        self._dir = os.path.dirname(__file__)

    @staticmethod
    def instance():
        if not hasattr(Captcha, "_instance"):
            Captcha._instance = Captcha()
        return Captcha._instance

    def initialize(self, width=400, height=180, color=None, text=None, fonts=None):
        """
        初始化验证码参数
        :param width: 图片宽度，默认400
        :param height: 图片高度，默认180（增加高度避免字符被裁剪）
        :param color: 文字颜色（RGB元组），若为None则随机生成深色
        :param text: 自定义验证码文本（若为None则随机生成）
        :param fonts: 字体文件路径列表
        """
        if text is None:
            # 生成4位验证码（字母+数字）
            self._text = ''.join(secrets.choice(SAFE_CHARS) for _ in range(4))
        else:
            self._text = text

        # 字体列表，优先使用系统字体，失败回退默认
        self.fonts = fonts if fonts else [
            os.path.join(self._dir, 'fonts', font) for font in DEFAULT_FONTS
        ]
        self.width = width
        self.height = height

        # 颜色对比度：背景浅色（200-255），文字深色（0-80）
        if color is None:
            pass
        else:
            self._color = color
        self._bg_color = self.random_color(200, 255)        # 浅色背景

    @staticmethod
    def random_color(start, end, opacity=None):
        red = random.randint(start, end)
        green = random.randint(start, end)
        blue = random.randint(start, end)
        if opacity is None:
            return red, green, blue
        return red, green, blue, opacity

    def background(self, image):
        """绘制纯色背景"""
        Draw(image).rectangle([(0, 0), image.size], fill=self._bg_color)
        return image

    @staticmethod
    def smooth(image):
        """平滑滤镜"""
        return image.filter(ImageFilter.SMOOTH)

    def curve(self, image, width=1, number=3, color=None):
        """绘制干扰曲线"""
        dx, height = image.size
        dx /= number
        path = [(dx * i, random.randint(0, height)) for i in range(1, number)]
        bcoefs = self._bezier.make_bezier(number - 1)
        points = []
        for coefs in bcoefs:
            points.append(tuple(sum([coef * p for coef, p in zip(coefs, ps)])
                                for ps in zip(*path)))
        Draw(image).line(points, fill=color if color else self._color, width=width)
        return image

    def noise(self, image, number=8, level=1, color=None):
        """绘制噪点（短线）"""
        width, height = image.size
        dx = width / 15
        width -= dx
        dy = height / 12
        height -= dy
        draw = Draw(image)
        for _ in range(number):
            x = int(random.uniform(dx, width))
            y = int(random.uniform(dy, height))
            draw.line(((x, y), (x + level, y)), fill=color if color else self._color, width=level)
        return image

    def random_dots(self, image, count=30, radius=1, color=None):
        """随机点状干扰（小圆点）"""
        draw = Draw(image)
        width, height = image.size
        for _ in range(count):
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                         fill=color or self._color)
        return image

    def random_lines(self, image, count=5, color=None):
        """绘制随机短线干扰"""
        draw = Draw(image)
        width, height = image.size
        for _ in range(count):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line((x1, y1, x2, y2), fill=color or self._color, width=random.randint(1, 2))
        return image

    def text(self, image, fonts, font_sizes=None, squeeze_factor=None, color=None, vertical_jitter=10):
        """
        使用锚点参数绘制验证码文字，并为每个字符添加微小垂直偏移
        :param image: PIL Image对象
        :param fonts: 字体文件路径列表
        :param font_sizes: 字体大小元组
        :param squeeze_factor: 字符间距压缩因子
        :param color: 文字颜色
        :param vertical_jitter: 垂直方向最大随机偏移量（像素）
        """
        global c_width
        color = color if color else self._color
        if font_sizes is None:
            font_sizes = self.font_sizes
        if squeeze_factor is None:
            squeeze_factor = getattr(self, 'squeeze_factor', 1.05)

        # 加载字体（尝试所有字体文件，随机选择）
        font_objects = []
        for name in fonts:
            for size in font_sizes:
                try:
                    font = truetype(name, size)
                    font_objects.append(font)
                except (OSError, IOError):
                    continue
        if not font_objects:
            # 无可用字体，使用默认字体
            font_objects = [ImageFont.load_default()]

        draw = Draw(image)

        # 计算总宽度，用于居中起始位置
        total_width = 0
        char_bboxes = []  # 存储每个字符的边界框
        for c in self._text:
            font = random.choice(font_objects)
            # 获取字符的边界框（兼容新旧 Pillow 版本）
            try:
                # Pillow >= 8.0 推荐使用 textbbox
                bbox = draw.textbbox((0, 0), c, font=font)
            except AttributeError:
                # 旧版使用 textsize
                width, height = draw.textsize(c, font=font)
                bbox = (0, 0, width, height)
            c_width = bbox[2] - bbox[0]
            c_height = bbox[3] - bbox[1]
            char_bboxes.append((bbox, c_width, c_height, font))
            total_width += c_width * squeeze_factor
        # 减去最后一个字符多余的 squeeze_factor 影响
        total_width -= c_width * (squeeze_factor - 1) if char_bboxes else 0

        # 水平起始位置（居中）
        start_x = (self.width - total_width) / 2
        x = start_x
        # 基准垂直位置（中间）
        base_y = self.height / 2

        for c, (bbox, c_width, c_height, font) in zip(self._text, char_bboxes):
            # 为每个字符生成随机垂直偏移（-vertical_jitter 到 +vertical_jitter）
            y_offset = random.randint(-vertical_jitter, vertical_jitter)
            center_y = base_y + y_offset

            # 使用锚点 'mm' 绘制字符（中心对齐）
            try:
                draw.text((x + c_width / 2, center_y), c, font=font, fill=color, anchor='mm')
            except TypeError:
                # 不支持锚点，使用传统偏移（垂直居中 + 抖动）
                y_pos = (self.height - c_height) // 2 + y_offset
                if y_pos < 0:
                    y_pos = 0
                draw.text((x, y_pos), c, font=font, fill=color)
            x += c_width * squeeze_factor

        return image

    def safe_rotate(self, image, max_angle=5, bg_color=None):
        if bg_color is None:
            bg_color = self._bg_color
        angle = random.uniform(-max_angle, max_angle)
        # 旋转时使用背景色填充扩展区域
        return image.rotate(angle, expand=True, fillcolor=bg_color)

    def safe_wave(self, image, amplitude=2, period=15, bg_color=None):
        if bg_color is None:
            bg_color = self._bg_color
        width, height = image.size
        result = Image.new('RGB', (width, height), bg_color)
        for y in range(height):
            dx = int(amplitude * math.sin(2 * math.pi * y / period))
            if dx == 0:
                row = image.crop((0, y, width, y+1))
                result.paste(row, (0, y))
            elif dx > 0:
                src = image.crop((0, y, width-dx, y+1))
                result.paste(src, (dx, y))
            else:
                src = image.crop((-dx, y, width, y+1))
                result.paste(src, (0, y))
        return result

    @staticmethod
    def _get_drawing_params(name):
        """返回扭曲方法的温和参数"""
        if name == 'offset':
            return {'dx_factor': 0.125, 'dy_factor': 0.15}
        elif name == 'warp':
            return {'dx_factor': 0.618, 'dy_factor': 0.125}
        elif name == 'wave':
            return {'amplitude': 3, 'period': 20}
        else:
            return {}

    @staticmethod
    def warp(image, dx_factor=0.125, dy_factor=0.258):
        """四边形扭曲"""
        width, height = image.size
        dx = width * dx_factor
        dy = height * dy_factor
        x1 = int(random.uniform(-dx, dx))
        y1 = int(random.uniform(-dy, dy))
        x2 = int(random.uniform(-dx, dx))
        y2 = int(random.uniform(-dy, dy))
        image2 = Image.new('RGB',
                           (width + abs(x1) + abs(x2),
                            height + abs(y1) + abs(y2)))
        image2.paste(image, (abs(x1), abs(y1)))
        width2, height2 = image2.size
        return image2.transform(
            (width, height), Image.QUAD,
            (x1, y1,
             -x1, height2 - y2,
             width2 + x2, height2 + y2,
             width2 - x2, -y1))

    @staticmethod
    def offset(image, dx_factor=0.05, dy_factor=0.05):
        """随机偏移（幅度极小）"""
        width, height = image.size
        dx = int(random.random() * width * dx_factor)
        dy = int(random.random() * height * dy_factor)
        image2 = Image.new('RGB', (width + dx, height + dy))
        image2.paste(image, (dx, dy))
        return image2

    @staticmethod
    def rotate(image, angle=25):
        """随机旋转"""
        return image.rotate(
            random.uniform(-angle, angle), Image.BILINEAR, expand=1)

    @staticmethod
    def wave(image, amplitude=4, period=25):
        """正弦波浪扭曲"""
        width, height = image.size
        result = Image.new('RGB', (width, height), (0, 0, 0))
        for y in range(height):
            dx = int(amplitude * math.sin(2 * math.pi * y / period))
            if dx == 0:
                row = image.crop((0, y, width, y + 1))
                result.paste(row, (0, y))
            else:
                if dx > 0:
                    src = image.crop((0, y, width - dx, y + 1))
                    result.paste(src, (dx, y))
                else:
                    src = image.crop((-dx, y, width, y + 1))
                    result.paste(src, (0, y))
        return result

    def captcha(self, path=None, fmt='PNG'):
        try:
            image = Image.new('RGB', (self.width, self.height), (255, 255, 255))
            image = self.background(image)

            # 绘制文字（每个字符增加垂直抖动）
            image = self.text(image, self.fonts, vertical_jitter=5)

            # 干扰：曲线（数量随机3~5，宽度随机1~2）
            curve_num = random.randint(3, 5)
            curve_width = random.randint(1, 2)
            image = self.curve(image, width=curve_width, number=curve_num)

            # 干扰：噪点（数量12~20，级别随机1~2）
            noise_num = random.randint(12, 20)
            noise_level = random.randint(1, 2)
            image = self.noise(image, number=noise_num, level=noise_level)

            # 干扰：随机短线（4~6条）
            line_num = random.randint(8, 16)
            image = self.random_lines(image, count=line_num)

            # 干扰：随机点状干扰（30~50个小圆点）
            dot_count = random.randint(50, 150)
            image = self.random_dots(image, count=dot_count, radius=1)

            # 轻微旋转（1~3度随机）
            image = self.safe_rotate(image, max_angle=3)

            # 轻微波浪扭曲（振幅1~2，周期15~20）
            wave_amp = random.randint(2, 3)
            wave_period = random.randint(15, 20)
            image = self.safe_wave(image, amplitude=wave_amp, period=wave_period)

            image = self.smooth(image)

            name = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(24))
            text = ''.join(self._text)

            out = BytesIO()
            if fmt.upper() == 'JPEG':
                image.save(out, format='JPEG', quality=95)
            else:
                image.save(out, format='PNG')

            if path:
                image.save(os.path.join(path, name), fmt)
            return name, text, out.getvalue()
        except Exception as e:
            import warnings
            warnings.warn(f"Captcha generation failed: {e}, using fallback")
            fallback_text = ''.join(secrets.choice(SAFE_CHARS) for _ in range(4))
            fallback_img = Image.new('RGB', (self.width, self.height), (255, 255, 255))
            draw = Draw(fallback_img)
            try:
                font = ImageFont.load_default()
            except:
                font = None
            draw.text((self.width//4, self.height//3), fallback_text, fill=(0,0,0), font=font)
            out = BytesIO()
            fallback_img.save(out, format='PNG')
            return "fallback", fallback_text, out.getvalue()

    def generate_captcha(self):
        """使用默认参数生成验证码"""
        self.initialize()
        return self.captcha("")


captcha = Captcha.instance()

if __name__ == '__main__':
    name, text, img_bytes = captcha.generate_captcha()
    print(f"Name: {name}, Text: {text}, Bytes length: {len(img_bytes)}")