from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextFieldRect
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivymd.uix.button import MDRectangleFlatButton, MDRaisedButton, MDFlatButton
from kivy.lang import Builder
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.dialog import MDDialog
from PIL import Image

mon = ''

class ScreenManager(ScreenManager):
    pass

class HomeScreen(Screen):
    
    def OpenManager(self):
        self.manager_open = False
        self.path = '/'
        self.file_manager = MDFileManager(exit_manager=self.exit_manager,select_path=self.select_path)

    def exit_manager(self):
        self.manager_open = False
        self.file_manager.close()

    def select_path(self, path):
        global mon
        mon = path
        self.exit_manager()
        toast(text=f'{mon.split("/")[-1]} Opened')

    def search_file(self):
        self.OpenManager()
        self.file_manager.show(self.path)
        self.manager_open = True

    def Startdecrypt(self):
        global mon
        self.decrypt(mon)

    def close_dialog(self,obj):
        self.dialog.dismiss()
    
    def decrypt(self,image_):
        print("decrypting",image_)
        img = image_
        image = Image.open(img, 'r')
        data = ''
        imgdata = iter(image.getdata())
        gather = True
        close_button = MDFlatButton(text='Close', on_release=self.close_dialog)
        Buttons = [close_button]
        while gather:
            pixels = [value for value in imgdata.__next__()[:3] +
                      imgdata.__next__()[:3] +
                      imgdata.__next__()[:3]]

            # string of binary data
            binstr = ''

            for i in pixels[:8]:
                if (i % 2 == 0):
                    binstr += '0'
                else:
                    binstr += '1'

            data += chr(int(binstr, 2))
            if (pixels[-1] % 2 != 0):
                self.dialog = MDDialog(title="Decoded Message",text=f"{data}", buttons=Buttons, size_hint=(0.95,1))
                gather = False
        self.dialog.open()

class EncodeScreen(Screen):
    

    def genBin(self, data):
        newd = []
        for i in data:
            newd.append(format(ord(i), '08b'))
        return newd

    def encrypt(self):
        img = mon
        image = Image.open(img, 'r')
        data = self.ids.message.text
        if (len(data) == 0):
            raise ValueError('Data is empty')
        newimg = image.copy()
        self.encode_new(newimg, data)
        new_img_name = self.ids.img_name.text
        namelen = len(mon.split("/")[-1])
        newimg.save(mon[:-(namelen)]+"/"+new_img_name, str(new_img_name.split(".")[1].upper()))
        toast(f'Image Encoded Succesfully And Saved As {new_img_name}')

    def modPix(self, pix, data):
        datalist = self.genBin(data)
        lendata = len(datalist)
        imdata = iter(pix)

        for i in range(lendata):
            # Extracting 3 pixels at a time
            pix = [value for value in imdata.__next__()[:3] +
                   imdata.__next__()[:3] +
                   imdata.__next__()[:3]]
            # Pixel value should be made odd for 1 and even for 0
            for j in range(0, 8):
                if (datalist[i][j] == '0' and pix[j] % 2 != 0):
                    pix[j] -= 1
                elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
                    if (pix[j] != 0):
                        pix[j] -= 1
                    else:
                        pix[j] += 1
            # Eighth pixel of every set tells
            # whether to stop ot read further.
            # 0 means keep reading; 1 means thec
            # message is over.
            if (i == lendata - 1):
                if (pix[-1] % 2 == 0):
                    if (pix[-1] != 0):
                        pix[-1] -= 1
                    else:
                        pix[-1] += 1
            else:
                if (pix[-1] % 2 != 0):
                    pix[-1] -= 1

            pix = tuple(pix)
            yield pix[0:3]
            yield pix[3:6]
            yield pix[6:9]

    def encode_new(self, newimg, data):
        w = newimg.size[0]
        (x, y) = (0, 0)

        for pixel in self.modPix(newimg.getdata(), data):

            # processed pixels in the new image
            newimg.putpixel((x, y), pixel)
            if (x == w - 1):
                x = 0
                y += 1
            else:
                x += 1

class MainApp(MDApp):
    def build(self):
        self.theme_cls.font_style = "JetBrainsMono"
        self.theme_cls.bg = self.theme_cls.bg_darkest
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.primary_hue = "500"
        master = Builder.load_file("main.kv")
        return master
    
MainApp().run()
