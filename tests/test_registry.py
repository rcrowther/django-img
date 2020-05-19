from django.test import TestCase

from image.registry import (
    FilterRegistry, 
    AlreadyRegistered, 
    Unregisterable,
    NotRegistered
)

from image.image_filters import Thumb

class NonFilter():
    pass
    
class TestFilterRegistry(TestCase):
    #! ignore non-image_config keys?
    def setUp(self):
        # Create a Registy for running tests on
        self.registry = FilterRegistry('test')

        # mock class to enter. NB, classes not instances
        self.filter = Thumb
        self.non_filter = NonFilter
        
    def test_register(self):
        self.registry.register(self.filter)
        self.assertEqual(self.registry.size, 1)

    def test_register_with_iterable(self):
        self.registry.register([self.filter])
        self.assertEqual(self.registry.size, 1)
                
    def test_register_non_filter_raises_unregisterable(self):
        with self.assertRaises(Unregisterable):
            self.registry.register(self.non_filter)

    def test_register_on_duplicate_key_raises_alreadyRegistered(self):
        self.registry.register(self.filter)
        with self.assertRaises(AlreadyRegistered):
            self.registry.register(self.filter)

    def test_call(self):
        self.registry.register(self.filter)
        r = self.registry(self.filter.human_id())
        self.assertTrue(isinstance(r, Thumb))        

    def test_register_call_missing_key_raises_notregistered(self):
        with self.assertRaises(NotRegistered):
            self.registry('stuff_n_nuff')
                            
    def test_unregister(self):
        self.registry.register(self.filter)
        self.registry.unregister(self.filter)
        self.assertEqual(self.registry.size, 0)


