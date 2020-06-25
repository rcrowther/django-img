from itertools import chain

from django.core import checks
#from django.contrib.admin.checks import BaseModelAdminChecks
f#rom django.forms import BaseForm
#from django.core.exceptions import FieldDoesNotExist
#from django.contrib.admin import checks as admincheck
from django.db import models
from inspect import isclass

from django.core.checks import Error, register
