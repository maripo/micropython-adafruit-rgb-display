import framebuf

FRAMEBUFF_TEXT_SIZE = 8

def text(display, text, x=0, y=0, size=8, color=0xffff, background=0x0000):
    lines = text.split('\n')
    x = min(display.width - 1, max(0, x))
    y = min(display.height - 1, max(0, y))
    rows = len(lines)
    cols = 0
    for line in lines:
        cols = max(cols, len(line))
    w = min(size * cols, display.width - x)
    h = min(size * rows, display.height - y)

    w_text = FRAMEBUFF_TEXT_SIZE * cols
    h_text = FRAMEBUFF_TEXT_SIZE * rows

    fb_text = framebuf.FrameBuffer(bytearray(w_text * h_text * 2), w_text, h_text, framebuf.RGB565)

    buffer_draw = bytearray(w * h * 2)
    fb_draw = framebuf.FrameBuffer(buffer_draw, w, h, framebuf.RGB565)
    fb_text.fill(background)
    text_y = 0
    for line in lines:
        fb_text.text(line, 0, text_y, color)
        text_y += FRAMEBUFF_TEXT_SIZE
    
    scale_ratio = FRAMEBUFF_TEXT_SIZE/size

    for buf_x in range(w):
        for buf_y in range(h):
            text_x = int(buf_x * scale_ratio)
            text_y = int(buf_y * scale_ratio)
            fb_draw.pixel(buf_x, buf_y, fb_text.pixel(text_x, text_y))
    
    display.blit_buffer(buffer_draw, x, y, w, h)
