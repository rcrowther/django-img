import unittest

from django.test import TestCase, SimpleTestCase
from django.template import Context, Template
from django.template import TemplateSyntaxError
from django.template.base import Token

from .mock_view import TestView
from image.models import Image
from image.image_filters import Thumb
from .utils import get_test_image_file_jpg



class TestTags(TestCase):
    # Check tags can output, and correctly.
    # Very difficult tests, currently done with inline templates.
    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)
        
    def setUp(self):
        self.image = Image.objects.create(
            title="Test",
            src=get_test_image_file_jpg(),
        )
        
        # Make reform explicitly so can delete files explicitly outside 
        # transactions.
        self.filter = Thumb()
        self.reform = self.image.get_reform(self.filter)

    def test_image_tag(self):
        render = self.render_template(
            '{% load img_tags %}{% image_tag image_model image.Thumb %}',
            context={'image_model': self.image}
            )
        self.assertHTMLEqual(render, '<img src="/media/reforms/test-image_thumb.png" alt="test image"/>')

    def test_image_tag_extra_attrs(self):
        render = self.render_template(
            '{% load img_tags %}{% image_tag image_model image.Thumb class="detail-img" %}',
            context={'image_model': self.image}
            )
        self.assertHTMLEqual(render, '<img src="/media/reforms/test-image_thumb.png" alt="test image" class="detail-img"/>')

    def tearDown(self):    
        self.reform.src.delete(False) 
        self.image.src.delete(False) 



from image.templatetags.img_tags import image_tag
from django.template.base import TokenType



class TestTagCalls(TestCase):
    # Basic tests that initial parameter checks are ok.
    # So calling the tag function directly with nearly no data. 
    def setUp(self):
        self.parser = None
 
    def test_not_enough_args_raises_templatesyntaxerror(self):
        token = Token(
            token_type = TokenType.TEXT,
            contents =  'image_tag image_model'
        )
        with self.assertRaises(TemplateSyntaxError):
            image_tag(self.parser, token)
        
    def test_malformed_kwargs_raises_templatesyntaxerror(self):
        token = Token(
            token_type = TokenType.TEXT,
            contents = 'image_tag image_model image.Thumb sth-pacific="True"'
        )
        with self.assertRaises(TemplateSyntaxError):
            image_tag(self.parser, token)
        
    def test_unquoted_kwargs_raises_templatesyntaxerror(self):
        token = Token(
            token_type = TokenType.TEXT,
            contents =  'image_tag image_model image.Thumb sthpacific=True'
        )
        with self.assertRaises(TemplateSyntaxError):        
            image_tag(self.parser,token)
