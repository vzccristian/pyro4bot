from PIL import ImageFont, ImageDraw, Image


def write_panel(val='0', list=[]):
    font_link = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
    font = ImageFont.truetype(font_link, size=130)
    img = Image.new('RGB', (200, 200), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((10, 40), val, fill=(255, 0, 0), font=font)
    font = ImageFont.truetype(font_link, size=20)
    i = 20
    for a in list:
        d.text((90, i), a, fill=(255, 0, 0), font=font)
        i += 32

    img.save("image.jpg")


if __name__ == '__main__':
    write_panel(list=['aaaaaa', 'bbbbbbb', 'cccccc', 'dddddd', 'eeeeeeee'])
