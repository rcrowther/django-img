from image import filters_wand, register

@register()
class Medium(filters_wand.ResizeSmart):
    width=260
    height=350
    format='jpg'
    jpeg_quality = 28
    pop = False
    greyscale=False
    night=False
    warm = False
    strong = False
    no=False
    film = False
    watermark = "image/watermark.png"
    
