import struct as ustruct
from rgb import DisplaySPI, color565

REG_MADCTL = 0x36

MADCTL_MY = 0x80  # Row Address Order
MADCTL_MX = 0x40  # Column Address Order
MADCTL_MV = 0x20  # Row / Column Exchange
MADCTL_ML = 0x10  # Vertical Refresh Order
MADCTL_BGR = 0x08 # RGB-BGR Order (0=RGB, 1=BGR)
MADCTL_MH = 0x04  # Horizontal Refresh Order

SCREEN_ROT_0DEG = 0
SCREEN_ROT_90DEG = 1
SCREEN_ROT_180DEG = 2
SCREEN_ROT_270DEG = 3

class ILI9341(DisplaySPI):
    """
    A simple driver for the ILI9341/ILI9340-based displays.


    >>> import ili9341
    >>> from machine import Pin, SPI
    >>> spi = SPI(mosi=Pin(13), sck=Pin(14))
    >>> display = ili9341.ILI9341(spi, cs=Pin(15), dc=Pin(12), rst=Pin(16))
    >>> display.fill(ili9341.color565(0xff, 0x11, 0x22))
    >>> display.pixel(120, 160, 0)
    """

    _COLUMN_SET = 0x2a
    _PAGE_SET = 0x2b
    _RAM_WRITE = 0x2c
    _RAM_READ = 0x2e
    _INIT = (
        (0xef, b'\x03\x80\x02'),
        (0xcf, b'\x00\xc1\x30'),
        (0xed, b'\x64\x03\x12\x81'),
        (0xe8, b'\x85\x00\x78'),
        (0xcb, b'\x39\x2c\x00\x34\x02'),
        (0xf7, b'\x20'),
        (0xea, b'\x00\x00'),
        (0xc0, b'\x23'),  # Power Control 1, VRH[5:0]
        (0xc1, b'\x10'),  # Power Control 2, SAP[2:0], BT[3:0]
        (0xc5, b'\x3e\x28'),  # VCM Control 1
        (0xc7, b'\x86'),  # VCM Control 2
        (0x36, b'\x48'),  # Memory Access Control
        (0x3a, b'\x55'),  # Pixel Format
        (0xb1, b'\x00\x18'),  # FRMCTR1
        (0xb6, b'\x08\x82\x27'),  # Display Function Control
        (0xf2, b'\x00'),  # 3Gamma Function Disable
        (0x26, b'\x01'),  # Gamma Curve Selected
        (0xe0,  # Set Gamma
         b'\x0f\x31\x2b\x0c\x0e\x08\x4e\xf1\x37\x07\x10\x03\x0e\x09\x00'),
        (0xe1,  # Set Gamma
         b'\x00\x0e\x14\x03\x11\x07\x31\xc1\x48\x08\x0f\x0c\x31\x36\x0f'),
        (0x11, None),
        (0x29, None),
    )
    _ENCODE_PIXEL = ">H"
    _ENCODE_POS = ">HH"
    _DECODE_PIXEL = ">BBB"

    def __init__(self, spi, dc, cs, rst=None, width=240, height=320):
        super().__init__(spi, dc, cs, rst, width, height)
        self.width_orig = width
        self.height_orig = height
        self._scroll = 0

    def scroll(self, dy=None):
        if dy is None:
            return self._scroll
        self._scroll = (self._scroll + dy) % self.height
        self._write(0x37, ustruct.pack('>H', self._scroll))

    def set_screen_rotation(self, rotation):
        val = MADCTL_BGR
        if rotation == SCREEN_ROT_0DEG:
            pass
        elif rotation == SCREEN_ROT_90DEG:
            val |= MADCTL_MV
        elif rotation == SCREEN_ROT_180DEG:
            val |= MADCTL_MY
        elif rotation == SCREEN_ROT_270DEG:
            val |= (MADCTL_MX | MADCTL_MY | MADCTL_MV)
        else:
            raise Exception("Invalid screen rotation")
        
        if rotation % 2 == 0:
            self.width = self.width_orig
            self.height = self.height_orig
        else:
            self.width = self.height_orig
            self.height = self.width_orig
        
        self._write(REG_MADCTL, bytearray([val]))
