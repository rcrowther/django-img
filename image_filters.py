import image


# Register your models here.
#@image.register
class Large(image.ResizeSmart):
    width=513
    height=760
 
 
#@image.register
class Medium(image.ResizeSmart):
    width=630
    height=272


#@image.register
class Small(image.ResizeSmart):
    width=128
    height=128

image.registry.register([Small, Medium, Large])
