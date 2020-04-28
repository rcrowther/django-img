from image import filters


# Register your models here.
#@image.register
class Large(filters.ResizeSmartFilter):
    width=513
    height=760
    iformat='png'


#@image.register
class Medium(filters.ResizeSmartFilter):
    width=630
    height=272
    iformat='png'


#@image.register
class Small(filters.ResizeSmartFilter):
    width=220
    height=292
    iformat='png'

