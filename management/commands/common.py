from image.models import Image, Reform
from django.core.management.base import CommandError
from django.apps import apps


def add_model_argument(parser):
        parser.add_argument(
            '-m',
            '--model',
            type=str,
            help='Target a model derived from Image, form:is <app.model>.',
        )

def get_model(options, allow_reform=False):
    # get or default the model to work with
    Model = Image
    model_path = options['model']        
    if (model_path):
        model_path_elements = model_path.split('.', 1)
        if (len(model_path_elements) != 2):
            raise CommandError("Unable to parse given app path: '{}'".format(model_path))
        try:
            Model = apps.get_model(model_path_elements[0], model_path_elements[1])
        except Exception as e:
            raise CommandError("Unable to locate given app path: '{}'".format(model_path))
        model_failed = (not issubclass(Model, Image))
        if (not allow_reform and model_failed):
            raise CommandError("Given class not a subclass of Image: '{}'".format(model_path))
        if (not issubclass(Model, Reform) and model_failed):
            raise CommandError("Given class not a subclass of Image or Reform: '{}'".format(model_path))
    return Model    
        
    
    
def add_contains_argument(parser):
    parser.add_argument(
        '-c',
        '--contains',
        type=str,
        help='Search for src-names containing this text',
    )
    
def filter_query_contains(options, queryset):
    return qs.filter(src__icontains=options["contains"])
