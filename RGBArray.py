import json
import re
import os
# ----- Assorted Data ----- #
class dataType:
    def __init__(self, name, size):
        self.name = name.upper()
        self.size = size

class tiffTag:
    def __init__(self, name, ID):
        self.name = name
        self.ID = ID

class tag:
    def __init__(self, tagData : tiffTag, dataType : dataType, valueCount : int, values):
        self.tagData = tagData
        self.dataType = dataType
        self.valueCount = valueCount
        self.values = values

# ----- Image files ----- #

class RGBArray:

    def __init__(self, fullcolRGBA: list[list[tuple]], width, height):
        self.RGBArray = fullcolRGBA
        self.width = width
        self.height = height
        with open("testppm.json", "w") as f:
            json.dump(self.RGBArray, f)

    def RGBArr2PPM(self, filepath: str):
        with open(filepath, "wb") as f:
            f.write("P6\n".encode())
            print(self.width, self.height)
            f.write((str(self.width) + "\n").encode())
            f.write((str(self.height) + "\n").encode())
            f.write("255\n".encode())
            for i in self.RGBArray:

                for r in i:
                    f.write(int.to_bytes(r[0], 1, byteorder="little"))
                    f.write(int.to_bytes(r[1], 1, byteorder="little"))
                    f.write(int.to_bytes(r[2], 1, byteorder="little"))

    def RGBArr2BMP(self, filepath: str):
        """Save as 32-bit BMP with alpha channel"""
        with open(filepath, "wb") as f:
            bytes_per_pixel = 4  # 32-bit BGRA
            row_bytes = self.width * bytes_per_pixel
            # No padding needed for 32-bit BMPs

            # Calculate sizes
            pixel_data_size = row_bytes * self.height
            dib_header_size = 40  # BITMAPINFOHEADER
            pixel_offset = 14 + dib_header_size
            file_size = pixel_offset + pixel_data_size

            # ----- BITMAP FILE HEADER -----
            f.write(b"BM")
            f.write(file_size.to_bytes(4, "little"))
            f.write((0).to_bytes(2, "little"))
            f.write((0).to_bytes(2, "little"))
            f.write(pixel_offset.to_bytes(4, "little"))

            # ----- DIB HEADER -----
            f.write(dib_header_size.to_bytes(4, "little"))
            f.write(self.width.to_bytes(4, "little"))
            f.write((-self.height).to_bytes(4, "little", signed=True))
            f.write((1).to_bytes(2, "little"))
            f.write((32).to_bytes(2, "little"))  # 32 bits per pixel
            f.write((0).to_bytes(4, "little"))  # BI_RGB (no alpha compression)
            # Note: For true alpha support, use BI_BITFIELDS (3) with masks
            f.write(pixel_data_size.to_bytes(4, "little"))
            f.write((2835).to_bytes(4, "little"))
            f.write((2835).to_bytes(4, "little"))
            f.write((0).to_bytes(4, "little"))
            f.write((0).to_bytes(4, "little"))

            # ----- PIXEL ARRAY (32-bit BGRA) -----
            for row in self.RGBArray:
                for pixel in row:
                    if len(pixel) == 4:
                        # RGBA to BGRA
                        b, g, r, a = pixel[2], pixel[1], pixel[0], pixel[3]
                        f.write(bytes([b, g, r, a]))
                    else:
                        # RGB to BGRA (add opaque alpha)
                        b, g, r = pixel[2], pixel[1], pixel[0]
                        f.write(bytes([b, g, r, 255]))


class BMP:

    def __init__(self, filepath):
        with open(filepath, "rb") as f:
            file = bytes(f.read())
            if file[0:2].decode() != "BM":
                print("Not a BMP file")

            # filesize
            self.sizehex = file[2:6].hex(" ")
            self.sizehex = "".join(reversed(self.sizehex.split()))
            print("File size:", round(int(self.sizehex, 16) / 1000000, 2), "MB")

            # offset of pixels
            self.offsethex = file[10:14].hex(" ")
            self.offsethex = "".join(reversed(self.offsethex.split()))
            print("Offset of pixel array:", int(self.offsethex, 16))

            self.DIBHeaderSize = file[14:18].hex(" ")
            self.DIBHeaderSize = "".join(reversed(self.DIBHeaderSize.split()))
            print("DIB Header Size:", int(self.DIBHeaderSize, 16))

            self.Width = file[18:22].hex(" ")
            self.Width = "".join(reversed(self.Width.split()))
            print("Img width:", int(self.Width, 16))

            self.Height = file[22:26].hex(" ")
            self.Height = "".join(reversed(self.Height.split()))
            print("Img height:", int(self.Height, 16))

            self.ColorPlanes = file[26:28].hex(" ")
            self.ColorPlanes = "".join(reversed(self.ColorPlanes.split()))
            print("Img color planes:", int(self.ColorPlanes, 16))

            self.BitsPerPixel = file[28:30].hex(" ")
            self.BitsPerPixel = "".join(reversed(self.BitsPerPixel.split()))
            print("Img bits per pixel:", int(self.BitsPerPixel, 16))

            self.CompressionMethod = file[30:34].hex(" ")
            self.CompressionMethod = "".join(reversed(self.CompressionMethod.split()))
            print("Img compression method:", int(self.CompressionMethod, 16))

            self.imgSize = file[34:38].hex(" ")
            self.imgSize = "".join(reversed(self.imgSize.split()))
            print("Img image size:", int(self.imgSize, 16))

            self.horizResolution = file[38:42].hex(" ")
            self.horizResolution = "".join(reversed(self.horizResolution.split()))
            print("Img horizontal resolution:", int(self.horizResolution, 16))

            self.verResolution = file[42:46].hex(" ")
            self.verResolution = "".join(reversed(self.verResolution.split()))
            print("Img vertical resolution:", int(self.verResolution, 16))

            self.impColors = file[46:50].hex(" ")
            self.impColors = "".join(reversed(self.impColors.split()))
            print("Important colors:", int(self.impColors, 16))
            self.RGB = []
            # colordata
            offset = int(self.offsethex, 16)
            width = int(self.Width, 16)
            height = int(self.Height, 16)
            row_bytes = width * 3
            padding = (4 - (row_bytes % 4)) % 4

            for h in range(height):
                self.RGB.append([])
                for i in range(width):
                    b = file[offset]
                    g = file[offset + 1]
                    r = file[offset + 2]
                    a = 255
                    self.RGB[h].append((r, g, b, a))
                    offset += 3
                offset += padding

    def BMP2RGBArr(self):

        return RGBArray(self.RGB[::-1], int(self.Width, 16), int(self.Height, 16))


class PPM:
    def __init__(self, filename):

        with open(filename, "rb") as f:
            file = bytes(f.read())
            if file[0:2].decode() == "P3":
                print("Currently only Binary PPM file is supported")
                self.type = 3
            elif file[0:2].decode() != "P6":
                print("Not a PPM file")
            else:
                validwhitespace = [" ", "\t", "\r", "\n", "\v", "\f"]
                cutfile = re.split("[" + "".join(validwhitespace) + "]", file.decode("ansi"))
                self.type = 6
                self.horizResolution = cutfile[1]
                self.verResolution = cutfile[2]
                self.maxColors = cutfile[3]
                offset = len("".join(cutfile[0:4])) + 4
                self.RGB = []
                for h in range(int(self.verResolution)):
                    self.RGB.append([])
                    for i in range(int(self.horizResolution)):
                        print(offset)
                        R = file[offset]
                        G = file[offset + 1]
                        B = file[offset + 2]
                        self.RGB[h].append((R, G, B))
                        offset+=3

    def PPM2RGBArr(self):
        return RGBArray(self.RGB, int(self.horizResolution), int(self.verResolution))

class TIFF:

    def __init__(self, filename):

        typeIntMap = {
            1:dataType("Byte", 1),
            2:dataType("Ascii", 1),
            3:dataType("Short", 2),
            4:dataType("Long", 4),
            5:dataType("Rational", 8),
            6:dataType("Sbyte", 1),
            7:dataType("Undefined", 1),
            8:dataType("Sshort", 2),
            9:dataType("Slong", 4),
            10:dataType("Srational", 8),
            11:dataType("Float", 4),
            12:dataType("Double", 8),
        }

        TIFF_TAGS = {
            254: tiffTag("NewSubfileType", 254),
            256: tiffTag("ImageWidth", 256),
            257: tiffTag("ImageLength", 257),
            258: tiffTag("BitsPerSample", 258),
            259: tiffTag("Compression", 259),
            262: tiffTag("PhotometricInterpretation", 262),
            273: tiffTag("StripOffsets", 273),
            274: tiffTag("Orientation", 274),
            277: tiffTag("SamplesPerPixel", 277),
            278: tiffTag("RowsPerStrip", 278),
            279: tiffTag("StripByteCounts", 279),
            282: tiffTag("XResolution", 282),
            283: tiffTag("YResolution", 283),
            284: tiffTag("PlanarConfiguration", 284),
            296: tiffTag("ResolutionUnit", 296),
            338: tiffTag("ExtraSamples", 338),
            34675: tiffTag("ICCProfile", 34675),
            # Optional / useful metadata tags
            270: tiffTag("ImageDescription", 270),
            271: tiffTag("Make", 271),
            272: tiffTag("Model", 272),
            305: tiffTag("Software", 305),
            306: tiffTag("DateTime", 306),
            0: tiffTag("Unrecognized", 0)
        }

        with open(filename, "rb") as f:
            file = f.read()
            if file[0:2].decode() not in ["II", "MM"]:
                print("Not a TIFF file")
                exit(1)

            self.byteorder = "little" if file[0:2].decode() == "II" else "big"

            print(self.byteorder)

            if int.from_bytes(file[2:4], byteorder=self.byteorder) != 42:
                print("Not a TIFF file")

            firstIFD = int.from_bytes(file[4:8], byteorder=self.byteorder)
            print(firstIFD)

            entryCount = int.from_bytes(file[firstIFD:firstIFD+2], byteorder=self.byteorder)
            print(entryCount)
            curroffset = firstIFD + 2
            for i in range(entryCount):

                # Tag read loop
                print()
                print("Tag",i)

                # gets tag ID from file and gets appropriate tiffTag class
                tagId = int.from_bytes(file[curroffset:curroffset+2], byteorder=self.byteorder)
                tagTitle = TIFF_TAGS[tagId].name if tagId in TIFF_TAGS else "Unrecognized"
                print("Tag ID", tagId)
                print("Tag Title:", tagTitle)
                curroffset += 2

                # gets the dataType from file and the appropriate dataType class
                datatype = typeIntMap[int.from_bytes(file[curroffset:curroffset+2], byteorder=self.byteorder)]
                print("Data Type:", datatype.name)
                curroffset += 2

                # gets the number of peices of data from the file
                count = int.from_bytes(file[curroffset:curroffset+4], byteorder=self.byteorder)
                print("Number of values:", count)
                curroffset += 4

                # gets the data/ offset from file
                val = int.from_bytes(file[curroffset:curroffset+4], byteorder=self.byteorder)
                print("Value/ Offset:", val)

                # checks if val is data or an offset
                if datatype.size * count > 4:

                    # val is an offset so split data accordingly
                    print("Object is too big therefore Value is an offset")
                    f.seek(val)
                    data = f.read(count*datatype.size)
                    n = datatype.size
                    val = [int.from_bytes(data[i:i + n], byteorder=self.byteorder) for i in range(0, len(data), n)]

                else:
                    # val is not an offset so split data accordingly
                    data = file[curroffset:curroffset + datatype.size * count]
                    n = datatype.size
                    val = [int.from_bytes(data[i:i + n], byteorder=self.byteorder) for i in range(0, len(data), n)]

                if len(val) == 1:
                    val = val[0]
                # creates tag object
                tagObj = tag(TIFF_TAGS[tagId if tagId in TIFF_TAGS else 0], datatype, count, val)
                setattr(self, tagObj.tagData.name, tagObj.values)
                curroffset += 4
            # checks if there are anymore tags
            if int.from_bytes(file[curroffset:curroffset+4], byteorder=self.byteorder) == 0:
                print("No more tags!")

            # Begin reading RGB Pixel data.
            # yay....
            print(self.SamplesPerPixel)
            if self.Compression != 1:
                print("Compression mode not supported")
                exit(1)

            elif self.SamplesPerPixel not in [3, 4] :
                print("Samples per pixel not supported")
                exit(1)
            self.RGBA = []
            for offset in self.StripOffsets:
                f.seek(offset)
                pixel_bytes = f.read(self.StripByteCounts[self.StripOffsets.index(offset)])
                pixel_size = sum(self.BitsPerSample) // 8
                pixels = [pixel_bytes[i:i + pixel_size] for i in range(0, len(pixel_bytes), pixel_size)]
                pixels = [tuple(b for b in p) for p in pixels]
                self.RGBA.append(pixels)

    def TIFF2RGBArr(self):
        return RGBArray(self.RGBA, self.ImageWidth, self.ImageLength)



TIFF("Example.tiff").TIFF2RGBArr().RGBArr2BMP("TIFF.bmp")
