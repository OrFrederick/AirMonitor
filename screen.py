import logging    
from waveshare_OLED import OLED_1in3
from PIL import Image, ImageDraw, ImageFont
from page import Page
from datetime import datetime
import config as cfg

class Screen:
    def __init__(self):
        print("starting screen")
        self.disp = OLED_1in3.OLED_1in3()
        self.disp.Init()
        self.disp.clear()
        
        self.W = self.disp.width
        self.H = self.disp.height    
        self.on = True        

        self.fonts = [ImageFont.truetype(cfg.FONTS + '/Exo-Medium.ttf', 12), ImageFont.truetype(cfg.FONTS + '/FredokaOne-Regular.ttf', 25), ImageFont.truetype(cfg.FONTS + '/Signika-Light.ttf', 15)]       
        (sw, sh) = (128, 64)
        dtime = datetime.now().strftime("%H:%M:%S")
        date = datetime.now().strftime("%d.%m.%Y")
        self.draw_page(Page([[(0,0),(sw-1,0)], [(0,0),(0,sh-1)], [(0,sh-1),(sw-1,sh-1)], [(sw-1,0),(sw-1, sh-1)]], [[(5, 3), dtime, 0], [(sw-65, 3), date,0], [self.get_center_coords(f"Loading...", 2), f"Loading...", 2]]))
    
    def get_center_coords(self, text, font):
        image = Image.new('1', (self.W, self.H), "WHITE")
        draw = ImageDraw.Draw(image)
        tw, th = draw.textsize(text, font=self.fonts[font])
        return ((self.W-tw) / 2, (self.H - th) / 2)
        
    def draw_page(self, page):
        image = Image.new('1', (self.W, self.H), "WHITE")

        draw = ImageDraw.Draw(image)
        
        for line in page.lines:
            draw.line(line, fill = 0)
        for txt in page.text:
            draw.text(txt[0], txt[1], font = self.fonts[txt[2]])
        image = image.rotate(180)
        self.disp.ShowImage(self.disp.getbuffer(image))    
    
    def __del__(self):
        OLED_1in3.config.module_exit()

