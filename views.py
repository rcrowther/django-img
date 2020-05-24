from django.forms import ModelForm
from myapp.models import Article

# Create the form class.
class ArticleForm(ModelForm):
     class Meta:
        model = Article
        fields = ['pub_date', 'headline', 'content', 'reporter']
