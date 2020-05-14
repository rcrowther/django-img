from django.test import TestCase
from image.settings import settings



class TestSettings(TestCase):
    # The class does a lot of checking itself. Without going overboard,
    # initialisation is all that needs checking.
    def setUp(self):
        self.settings = settings
