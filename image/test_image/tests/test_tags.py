import unittest
from django.test import TestCase
from django.template import Context, Template
from django.template import TemplateSyntaxError
from django.template.base import Token

#from test_image.models import TestImage
from image.image_filters import Thumb
from . import utils



from image.templatetags.img_tags import image_tag, query_tag
from django.template.base import TokenType



# ./manage.py test image.tests.test_tags
class TestImageTagCalls(TestCase):
    # Basic tests that initial parameter checks are ok.
    # So calling the tag function directly with nearly no data. 
    def setUp(self):
        self.parser = None
 
    def test_not_enough_args_raises_templatesyntaxerror(self):
        token = Token(
            token_type = TokenType.TEXT,
            contents =  'image image_model'
        )
        with self.assertRaises(TemplateSyntaxError):
            image_tag(self.parser, token)
        
    def test_malformed_kwargs_raises_templatesyntaxerror(self):
        token = Token(
            token_type = TokenType.TEXT,
            contents = 'image image_model image.Thumb sth-pacific="True"'
        )
        with self.assertRaises(TemplateSyntaxError):
            image_tag(self.parser, token)
        
    def test_unquoted_kwargs_raises_templatesyntaxerror(self):
        token = Token(
            token_type = TokenType.TEXT,
            contents =  'image image_model image.Thumb sthpacific=True'
        )
        with self.assertRaises(TemplateSyntaxError):        
            image_tag(self.parser,token)



class TestQueryTagCalls(TestCase):
    # Basic tests that initial parameter checks are ok.
    # So calling the tag function directly with nearly no data. 
    def setUp(self):
        self.parser = None
 
    def test_not_enough_args_raises_templatesyntaxerror(self):
        token = Token(
            token_type = TokenType.TEXT,
            contents =  'imagequery image_model "query"'
        )
        with self.assertRaises(TemplateSyntaxError):
            query_tag(self.parser, token)
        
    def test_malformed_kwargs_raises_templatesyntaxerror(self):
        token = Token(
            token_type = TokenType.TEXT,
            contents = 'imagequery image_model "query" image.Thumb sth-pacific="True"'
        )
        with self.assertRaises(TemplateSyntaxError):
            query_tag(self.parser, token)

    def test_unquoted_query_raises_templatesyntaxerror(self):
        token = Token(
            token_type = TokenType.TEXT,
            contents =  'imagequery image_model query image.Thumb sthpacific="True"'
        )
        with self.assertRaises(TemplateSyntaxError):        
            query_tag(self.parser,token)
                    
    def test_unquoted_kwargs_raises_templatesyntaxerror(self):
        token = Token(
            token_type = TokenType.TEXT,
            contents =  'imagequery image_model "query" image.Thumb sthpacific=True'
        )
        with self.assertRaises(TemplateSyntaxError):        
            query_tag(self.parser,token)            
            
            
            
class TestTags(TestCase):
    # Check tags can output, and correctly.
    # Difficult tests, currently done with inline templates.
    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)
        
    def setUp(self):
        self.image = utils.get_test_image()
        
        # Make reform explicitly so can delete files explicitly outside 
        # transactions.
        self.filter = Thumb()
        self.reform = self.image.get_reform(self.filter)

    def test_image_tag(self):
        render = self.render_template(
            '{% load img_tags %}{% image image_model image.Thumb %}',
            context={'image_model': self.image}
            )
        self.assertHTMLEqual(render, '<img src="/media/test_reforms/test-image_thumb.png" alt="test image"/>')

    def test_image_tag_extra_attrs(self):
        render = self.render_template(
            '{% load img_tags %}{% image image_model image.Thumb class="detail-img" %}',
            context={'image_model': self.image}
            )
        self.assertHTMLEqual(render, '<img src="/media/test_reforms/test-image_thumb.png" alt="test image" class="detail-img"/>')

    def test_image_query_tag(self):
        render = self.render_template(
            '{% load img_tags %}{% imagequery test_image.TestImage "pk=1" image.Thumb %}',
            context={}
            )
        self.assertHTMLEqual(render, '<img src="/media/test_reforms/test-image_thumb.png" alt="test image"/>')

    def tearDown(self):    
        self.reform.src.delete(False) 
        utils.image_delete(self.image)


