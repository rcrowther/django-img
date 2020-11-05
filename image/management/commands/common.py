from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import CommandError
from image import module_utils


def add_model_argument(parser):
        parser.add_argument(
            'model',
            type=str,
            help='Target a model derived from AbstractImage, form:is <app.model>.',
        )
        
def get_image_model(options):
    model_path = options['model']        
    try:
        Image = module_utils.get_image_model(model_path)
    except ImproperlyConfigured as e:

        # Stock exception system not working for this
        raise  CommandError(e.args[0])
    return Image

def get_reform_model(options):
    model_path = options['model']
    try:
        Reform = module_utils.get_reform_model(model_path)
    except ImproperlyConfigured as e:

        # Stock exception system not working for this
        raise  CommandError(e.args[0])
    return Reform

            
def add_contains_argument(parser):
    parser.add_argument(
        '-c',
        '--contains',
        type=str,
        help='Search for src-names containing this text',
    )
    
def filter_query_contains(options, queryset):
    if (options["contains"]):
        queryset = queryset.filter(src__icontains=options["contains"])
    return queryset
