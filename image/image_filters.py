from image import filters_pillow, register, registry



#@register()
class Thumb(filters_pillow.ResizeSmart):
    width=64
    height=64
    format='png'

registry.register(Thumb)
