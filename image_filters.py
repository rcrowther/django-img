from image import filters_pillow
from image import filters_wand, registry

# Register models here,
#! Probably only Thumb makes any sense....
#@image.register
# class Large(filters_pillow.CropSmart):
    # width=513
    # height=760

# class Large(filters_wand.ResizeSmart):
    # width=513
    # height=760
    # pop = True
    # greyscale=False
    # night= False
    # warm = False
    # strong = False
    # no = False
    # watermark = None #'/srv/images/watermark.png'
    # fill_color="goldenrod"
  
 
# #@image.register
# class Medium(filters_pillow.ResizeSmart):
    # width=630
    # height=272


# #@image.register
# class Small(filters_pillow.ResizeSmart):
    # width=128
    # height=128
    

#@image.register
class Thumb(filters_pillow.ResizeSmart):
    width=64
    height=64
    iformat='png'
    #fill_color="darkgreen"
    
# class Level(filters_wand.Level):
    # black_level = 0.2
    # white_level = 0.9
    # gamma = 0.95

# class Format(filters_wand.Format):
    # # black_level = 0.2
    # # white_level = 0.9
    # #format ='jpg'
    # jpeg_quality = 85
    # pop = False
    # greyscale=False
    # cool= False
    # warm = False
    # strong = False
    # film = False
    
# class SmallWand(filters_wand.Resize):
    # width=180
    # height=180
                
#registry.register([Format, Small, Medium, Large, Thumb, SmallWand])
registry.register(Thumb)