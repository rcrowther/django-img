from django import template
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt
from django.core.exceptions import ImproperlyConfigured

#from django.utils.functional import cached_property
from image.models import Image
from image.shortcuts import get_reform_or_not_found
from image.registry import registry

register = template.Library()



def filter_id_resolve(filter_id):
    '''
    Take a module path supplied by the coder, and return in a form
    usuable by the registry. 
    Module paths are supplied by the co
    '''
    # NB: filter registry keys remove the 'image_filters' module part.
    # A coder will guess or be told this.
    # Cheap test works unless the coder buries the image_filters' file.
    # in which case, it's resonable to ask for a full path.
    if (filter_id.find('.') == -1):
        # The path has been abreviated to assume the current app, which
        # must be derived from the context.
        view = context.get('view')

        # 'view' is present on any Django template view, so resonably safe
        # to look for. In case there is some sly tampering, or edge 
        # usecase, though the message is unhelpful...
        if (not(view)):
            raise ImproperlyConfigured("A short filter reference has been provided, but the template context has no view to supply a full path. filter_id:{}".format(
                filter_id,
            ))
        #print(str(view.__module__))
        app_name = view.__module__.split('.', 1)[0]
        filter_id = app_name + '.' + filter_id
    return filter_id
    
        
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
    im = Image.objects.get(title=img_title)
    # if cant find matching filter, allow errors to throw.
    ifilter = registry(filter_id_resolve(filter_id))
    r = get_reform_or_not_found(im, ifilter)
    return r.img_tag(kwargs)


       
# @register.simple_tag(takes_context=True)
# def image_tag(context, img_model, filter_id, **kwargs):



class ImageNode(template.Node):
    def __init__(self, image_model, filter_id, kwargs):
        self.image = template.Variable(image_model)
        self.filter = registry(filter_id_resolve(filter_id))      
        self.kwargs = kwargs
        
    def render(self, context):
        try:
            im = self.image.resolve(context)
            reform = get_reform_or_not_found(im, self.filter)
            attrs = reform.attrs_dict.copy()
            attrs.update(self.kwargs)
            return mark_safe('<img {} />'.format(flatatt(attrs)))
        except template.VariableDoesNotExist:
            return ''
        
        
from django.template.base import kwarg_re
@register.tag(name="image_tag")
def image_tag(parser, token):
    '''
    Lookup and display an image. 
    Search is by image details, passed in a context, and filter id.
    If a view has already generated a context with models, this is the
    prefered method.
    
    image_model 
        reference to an image in the template context (NB: 
    the parameter can handle dotted notation e.g. page.image)
    
    filter_id 
        string module path to a Filter e.g. "image.Format". If 
    the Filter only is named, the app location of the calling view is 
    added e.g. if "Large" is called from a view in 'page', the filter 
    becomes "page.Large"
     
    kwargs 
        Will be added as attribut4es to the final tag.
    ''' 

    lumps = token.split_contents()

    if(len(lumps) < 3):
        raise template.TemplateSyntaxError(
            "Image tag needs two arguments. tag:{}".format(
                token.contents,
            ))
            
    tag_name = lumps[0]
    image_model = lumps[1]
    filter_id = lumps[2]
    
    # Could look at templates.base.token_kwargs(),
    # but KISS    
    kwlumps = lumps[3:]
    kwargs = {}

    # Tag is tokenizing is from strings, and that depends on 
    # quotes for whitespace and separation.
    # However, the result must be quote-stripped for flatattr() to do
    # it's Django-compliant job in ImageNode.
    # (It might be nice to do further parsing on keyword values, to 
    # allow vars and so forth. But in this atmosphere...)   
    for kw in kwlumps:
        match = kwarg_re.match(kw)
        if not match:
            raise template.TemplateSyntaxError("Malformed arguments to image tag. tag:{} kw:{}".format(
               token.contents,
               kw
           ))
        k, v = match.groups()
        if not (v[0] == v[-1] and v[0] in ('"', "'")):
           raise template.TemplateSyntaxError(
               "image tag keyword arguments should be in quotes. token:{} kw:{}".format(
               token.contents,
               kw
           ))
        kwargs[k] = v[1:-1]

    return ImageNode(image_model, filter_id, kwargs)


    
@register.simple_tag(takes_context=True)
def image_url(context, img_model, filter_id):
    im = context['review'].img
    # if cant find matching filter, allow errors to throw.
    ifilter = registry(filter_id_resolve(filter_id))  
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
 
