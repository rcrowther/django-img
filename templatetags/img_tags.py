from django import template
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt

#from django.utils.functional import cached_property
#from image.utils import get_image
from image.models import Image
# template?
# as url/static
#tmp, until we have registry
from image.image_filters import Small
from image.registry import registry

register = template.Library()

'''You can do one of two ways. Either 
- take an image from an item in a context
{% image_tag review.img, Large, class='header-image' %}
- take an image title
{% image_tag_by_title 'dirty_river', Large, class='header-image' %}
''' 
'''
Lookup an image by reform (filter) and title.
If a view has already generated a context with models, this is not 
a prefered method, as it will make an extra database lookup.
'''
@register.simple_tag
def image_tag_by_title(img_title, ifilter, **kwargs):
    print('image_tag_by_title:')
    print(str(img_title))
    print(str(ifilter))
    #print('context in temlate tag:')
    #print(str(context))
    #img_title = 'phone'
    im = Image.objects.get(title=img_title)
    f = registry.get_instance(ifilter)
    #f = Small()
    r = im.get_reform(f)
    return r.img_tag(kwargs)


'''
Lookup an image by reform (filter), context and reference.
If a view has already generated a context with models, this is the
prefered method.
'''        
@register.simple_tag(takes_context=True)
def image_tag(context, img_model, ifilter, **kwargs):
    # split context reference to delve context?

    print('image in temlate tag:')
    print(str(img_model))
    print('context in temlate tag:')
    print(str(context))
    
    obj_key = 'object'
    obj = context[obj_key]
    im = obj.img
    f = registry.get(ifilter)
    #f = Small()
    r = im.get_reform(f)
    flatatt(kwargs)
    return r.url()
        
@register.simple_tag(takes_context=True)
def image_url(context, img_model, ifilter):
    im = context['review'].img
    r = im.get_reform(Small())
    return r.url()
        
# {% image_tag 'dirty_river', Large, class='header-image' %}
# @register.tag(name="image-tag")
# def image_tag(img_name, filter_name, static_access, **kwargs):
    # '''kwargs used for image tag attributes. static_access allows a local override of the IMAGE_STATIC_ACCESS setting.'''
    # #test inputs
    
    # r = get_filter(filter_name)
    # Images.objects
    # image = get_image(img_name)
    # r.process(image)
    # return r.img_tag(static_or_url, kwargs)
 
