class RGBArray():

    def __init__(self, fullcolRGBA : list[list[tuple]], width, height):
        self.RGBArray = fullcolRGBA
        self.width = width
        self.height = height

class BMP:

    def __init__(self,filepath):
        with open(filepath, 'rb') as file:
            full = bytes(file.read())

        print(full[0:2])


BMP("Test.bmp")