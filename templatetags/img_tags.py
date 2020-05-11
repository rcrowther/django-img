from django import template
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt

#from django.utils.functional import cached_property
#from image.utils import get_image
from image.models import Image
# template?
# as url/static
#tmp, until we have registry
#from image.image_filters import Small
from image.registry import registry
from image import utils
from image.shortcuts import get_reform_or_not_found


register = template.Library()

'''You can do one of two ways. Either 
- take an image from an item in a context
{% image_tag review.img, Large, class='header-image' %}
- take an image title
{% image_tag_by_title 'dirty_river', Large, class='header-image' %}
''' 

@register.simple_tag(takes_context=True)
def image_tag_by_title(context, img_title, filter_id, **kwargs):
    '''
    Lookup an image by filter, and title.
    If a view has already generated a context with models, this is not 
    a prefered method, as it makes a database lookup.
    @img_title string reference to an image by title e.g. 'taunton_skyscraper'
    @filter_id string module path to a Filter e.g. "image.Format". If 
    the Filter is only named, the app location of the calling view is 
    added e.g. if "Large" is called from a view in 'page', the filter 
    become "page.Large" 
    @kwargs added as attribut4es to the final tag.
    ''' 
    # print('image_tag_by_title:')
    # print(str(img_title))
    # print(str(filter_id))
    # print('context in temlate tag:')
    # print(str(img_title))
    #! pass this in
    #img_title = 'phone'
    im = Image.objects.get(title=img_title)
    # expand abreviated filter paths
    if (filter_id.find('.') == -1):
        view_path = context.get('view').__module__
        #print(str(view_path))
        filter_id = utils.ModulePath(view_path).root.extend(filter_id)
    ifilter = registry.get_instance(filter_id)
    r = get_reform_or_not_found(im, ifilter)
    return r.img_tag(kwargs)


       
@register.simple_tag(takes_context=True)
def image_tag(context, img_model, filter_id, **kwargs):
    '''
    Lookup an image by reform (filter), context and reference.
    If a view has already generated a context with models, this is the
    prefered method.
    @img_model reference to an image in the template context (NB 
    templates can handle dotted notation e.g. page.image)
    @filter_id string module path to a Filter e.g. "image.Format". If 
    the Filter is only named, the app location of the calling view is 
    added e.g. if "Large" is called from a view in 'page', the filter 
    become "page.Large" 
    @kwargs added as attribut4es to the final tag.
    ''' 
    #! data recovery needs help
    #! how template tags do dotted notation? Do they?
    print('image in temlate tag:')
    print(str(img_model))
    #print('context in temlate tag:')
    #print(str(context))
    
    obj_key = 'object'
    obj = context[obj_key]
    im = obj.img
    # expand abreviated filter paths
    if (filter_id.find('.') == -1):
        view_path = context.get('view').__module__
        #print(str(view_path))
        filter_id = utils.ModulePath(view_path).root.extend(filter_id)
    #print('ifilter in temlate tag:')
    #print(str(ifilter))        
    ifilter = registry.get_instance(filter_id)
    r = get_reform_or_not_found(im, ifilter)
    return r.img_tag(kwargs)
        
        
@register.simple_tag(takes_context=True)
def image_url(context, img_model, filter_id):
    im = context['review'].img
    if (filter_id.find('.') == -1):
        view_path = context.get('view').__module__
        #print(str(view_path))
        filter_id = utils.ModulePath(view_path).root.extend(filter_id)    
    f = registry.get_instance(filter_id)
    ifilter = registry.get_instance(filter_id)
    r = get_reform_or_not_found(im, ifilter)
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
 
