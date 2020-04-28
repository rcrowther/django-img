from image import filters


# Register your models here.
#@image.register
class Large(filters.ResizeSmart):
    width=513
    height=760
    iformat='png'


#@image.register
class Medium(filters.ResizeSmart):
    width=630
    height=272
    iformat='png'


#@image.register
class Small(filters.ResizeSmart):
    width=128
    height=128
    iformat='jpg'

