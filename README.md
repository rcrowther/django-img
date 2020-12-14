# Django-img
An app to handle upload and display of images.

The app needs at least one repository declaring then a migration. After declaring an admin, upload is possible. To show images, only a few filter classes are needed (some are builtin), and to place the main template tag. That's all.

The base code is concise and levers Django recommendations and facilities where possible. It may provide a base for others wishing to build their own app.

The distribution is called 'django-img', but internally the module is called 'image'.

This is [a rewrite of Wagtail's Image app](#credits).

## Why you may or may not want this app
This may not be the app for you,

Pro
- Abstract base allows any number of repositories with custom configurations
- Filter declarations can travel with apps (like CSS)
- Auto-generates filtered images
- One (primary) template tag

Con
- Only images, not any file
- Filters can not be applied to individual images
- No effort to present filters to users, either admin or visitors
- No builtin categorisation and/or tagging

You can, by targeting in templates, apply a special filter to one image, but the system is geared towards handling images in classes.
 
The idea is to step back from flexible chain presentation and APIs. All most sites need is to upload images, crop to size, then run some general image enhancement. By dropping APIs and configuration the app is small, concise, and fits good CSS/template-practice. 

Also, I have not,
- considered SVG images or movie files
- tested cloud storage


## Overview
![overview diagram](screenshots/overview.svg?raw=true&sanitize=true)

Images are tracked in the database. The base model is called 'AbstractImage'. 

Each original image can generate derivative images. These are tracked by models based in 'AbstractReform'. Reforms are generated by filters. Filters can be defined in apps or centrally. 

Image delivery is by template tag. The presence of a tag with a reference to an image and a filter will generate a reform automatically. The tags deliver images by URL.

File-based storage is in 'media/' with paths adjustable through attribute settings.

The app includes code to upload images. Some custom Django admin is provided, which is optional and easy to modify/replace.



## If you have done this before
- [subclass the models for Image and Reform](#custom-image-repositories) to create a repository.
- Migrate custom repository tables
- [Add fields](#model-fields) to models that need them
- Migrate models carrying image fields
- Create 'image_filters.py' files in the apps, then [subclass a few filters](#filters)
- Insert [template tags](#template-tags) into relevant templates



## Quickstart
### Depemdancies
Unidecode,

    pip unidecode

[Unidecode](https://pypi.org/project/Unidecode/)

Pillow,

    pip pillow

[Pillow](https://pillow.readthedocs.io/en/stable/index.html)


#### Optional
To use Wand filters, on Debian-based distros,

    sudo apt-get install libmagickwand-dev

Then,

    pip install wand





### Install
PyPi,

    pip install django-img

Or download the app code to Django.

Declare in Django settings,

        INSTALLED_APPS = [
            ...
            'image.apps.ImageConfig',
            ...
        ]

Migrate,

    ./manage.py makemigrations image
    ./manage.py migrate image

If you have Django Admin, you can now upload images.



### Upload some images
In Django admin, go to Image upload and upload a few images.

I don't know about you, but if I have a new app I like to try with real data. If you have a collection of test images somewhere, try this management command,

    ./manage.py image_create_bulk pathToMyDirectory

You can create, meaning upload and register, fifteen or twenty images in a few seconds.



### View some images
Ok, let's see an image. Two ways,

#### Use a view 
Find a web view template. Nearly any template will do (maybe not a JSON REST interface, something visible).

Add this tag to the template,

    {% load img_tags %}
    ...
    {% imagequery image.Image "pk=1" image.Thumb %}

'image.Thumb' is a predefined filter. It makes a 64x64 pixel thumbnail. The tag we use here searches for an image by a very low method, "pk=1". This will do for now. 

Visit the page. The app will generate the filtered 'reform' image automatically.


#### Don't have a view?
Yeh, new or experimental site, I know. Image has a builtin template. [Make a view](#the-view). Now visit (probably) http://localhost:8000/image/1/ To see some *real* web code.



### (optional) See a broken image
Use the management command to remove reforms,

    ./manage.py reform_delete

No better way to make a truly broken file... Goto '/media/originals' and delete a file (maybe the file you are currently viewing as a reform). 

Now refresh the view. The app will try to find the reform. When it fails, it will attempt to make a new reform. But the original file is missing, so it will fail to do that too. It will then display a generic 'broken' image.
 
### (aside) Filters
Perhaps your first request will be how to make a new filter.

Make a new file called 'image_filters'. Put it in the top level of any app (not in the site directory, that can be done but must be configured in a [settings.py](#settings). Put something in like this (adapt if you wish),

    from image import Resize, registry

    class MediumImage(Resize)
        width=260
        height=350
        format='png'

    registry.register(MediumImage)
 
Now adapt the template tag (or the tag in 'image/templates/image/image_detail.html') to point at the new filter,

    {% imagequery image.Image "pk=1" someAppName.MediumImage %}

Visit the page again. Image uses the new filter definition to generate a new reform (filters the image) then displays it.

Ok, you changed the image size, and maybe the format. If you want to continue, you probably have questions. Goto the main documentation.



## QuickStop
Don't like what you see?

- Remove any temporary code.
- Migrate backwards ('./manage.py migrate image zero')
- Remove from 'apps.py'
- Remove the two directories '/media/originals/', '/media/reforms/'
- Remove the app folder, or uninstall

That's it, gone.



## Full documentation
Index, 

- [Model Fields](#model-fields)
- [New Image Repositories](#custom-image-repositories)
- [Auto Delete](#auto-delete)
- [Filters](#filters)
- [Admin](#admin)
- [Forms](#forms)
- [Template Tags](#template-tags)
- [Management Commands](#management-commands)
- [Settings](#settings)
- [Utils](#utilities)
- [Tests](#tests)


## Model Fields
Two ways,

#### Custom ImageRelationFieldMixin fields
There are two, ImageOneToOneField and ImageManyToOneField (for image pools),

    from image.model_fields import ImageManyToOneField


    class Page(models.Model):

        img = ImageManyToOneField(
            'page.Image'
            )


##### Auto-delete images
An ImageOneToOneField field can auto-delete associated Image models and files (and their reforms) with the model. See [Auto Delete](#auto-delete) 


#### Stock Django
You can also use a Django foreign key declaration,

    from image.models import Image


    class Page(models.Model):

        img = models.ForeignKey(
            'page.Image',
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name='+'
            )

         etc.

null=True and blank=True means users can delay adding an image until later. And related_name='*' means that Images will not track the models you are creating. See Django documentation of model fields for more details.

Only use models.CASCADE if you are sure this is what you want. It means, if an image is deleted, the model that carries the image is deleted too. This is not usually what you want.


#### Choosing between the two
ImageOneToOneField/ImageManyToOneField
- tidy
- Works with preconfigured admin and auto-delete

Foreign Field
- Django stock
- explicit
- flexible configuration


## Image Repositories
### Overview
New repositories can be made by subclassing the the core models.

Reasons you may want to customise repositories,

#### Repository behaviour
Custom repositories have new DB tables, and can operate with new configurations such as storing files in different directories, auto-deleting original files, not limiting filename sizes and more.

#### Associate data with images
You may want to associate data with an image. Many people's first thought would be to add a title, as the app does not provide titles by default. But other kinds of information can be attached to an image such as captions, credits, dates, and/or data for semantic/SEO rendering.

#### Split needs
For example, you may want a repository attached to a main Article model, and also an image pool for general site use such as banners or icons. 
 

### Subclassing Image/Reform 
Custom Image repository code is placed in 'models.py' files and migrated. You decide how you want your namespacing to work. The code can be placed in an app handling one kind of model or, for general use, in a separate app.

Here is a minimal subclass. In the 'models.py' file in an app, do this,

    from image.models import AbstractImage, AbstractReform

    class NewsArticleImage(AbstractImage):
        reform_model = 'NewsArticleReform'
        upload_dir='news_originals'

        # AbstractImage has a file and upload_date
        caption = models.CharField(_('Caption'),
            max_length=255,
        )

        author = models.CharField(_('Author'),
            max_length=255,
            db_index=True
        )

        etc.



    class NewsArticleReform(AbstractReform):
        image_model = NewsArticleImage
        upload_dir='news_reforms'

        # exactly the same in every subclass
        image = models.ForeignKey(image_model, related_name='+', on_delete=models.CASCADE)


Not the last word in DRY coding, but you should be able to work out what the code is for. Note that 'image_model' and 'reform_model' are explicitly declared. Note also that 'reform_model' is declared as a string, but 'image_model' is declared as a class.

Migrate,

    ./manage.py makemigrations NewsArticle
    ./manage.py migrate NewsArticle

You now have a new image upload app. It has it's own DB tables. Change it's configuration (see next section). Refer to it in other models,

    class NewsArticle(models.Model):

        img = ImageManyToOneField(
            "news_article.NewssArticleImage"
            )

        etc.

### Attributes
Subclasses accept some attributes. Note that some of these settings are radical alterations to a model class. To be sure a model setting will take effect, it is best to migrate the class.

An expanded version of the above,

    from image.models import AbstractImage, AbstractReform

    class NewsArticleImage(AbstractImage):
        reform_model = 'NewsArticleReform'
        upload_dir='news_originals'
        accept_formats = ['png']
        filepath_length=55
        max_upload_size=2
        form_limit_filepath_length=True
        auto_delete_files=True

        ...



    class NewsArticleReform(AbstractReform):
        image_model = NewsArticleImage
        upload_dir='news_reforms'
        file_format='png'
        jpeg_quality=28

        # exactly the same in every subclass
        image = models.ForeignKey(image_model, related_name='+', on_delete=models.CASCADE)

Some of these attributes introduce checks ('max_upload_size'), some set defaults('file_format'), some can be overridden ('file_format', 'jpeg_quality' can be overridden by filter settings) (the configuration above is odd, and for illustration. If reforms are set to 'file_format'='png', 'jpeg_quality' is unlikely ever to be used). See [Settings](#settings) for details.

Migrate, and you are up and running.


### Inheritance! Can I build repositories using OOP techniques?
No! Python has been cautious about this kind of programming, and Django's solutions are a workround. Try stacking models of any kind and, unless you know the code line by line, the classes will create unusable migrations. In the current situation, for stability and maintainability, create models directly from the two abstract bases.

### Can I create different repositories, then point them at the same storage paths?
The app tracks through the database tables, and the [management commands](#management-commands) work from them, so yes, you can. That said, when code offers opportunities for namespacing/encapsulation, you need a good reason to ignore it.

### Things to consider when subclassing models

#### Auto delete of files
May be good to set up your deletion policy from the start. See [Auto Delete](#auto-delete)
 
#### Add Meta information
You may want to configure a Meta class. If you added titles or slugs, for example, you may be interested in making them into unique constrained groups, or adding indexes,

    class NewssArticleImage(AbstractImage):
        upload_dir='news_originals'
        filepath_length=100

        etc.

        class Meta:
            verbose_name = _('news_image')
            verbose_name_plural = _('news_images')
            indexes = [
                models.Index(fields=['author']),
            ]
            constraints = [
                models.UniqueConstraint(
                    fields=['title', 'author'], 
                    name='unique_newsarticle_reform_src'
                )
            indexes = [
                models.Index(fields=['upload_time']),
            ]

Note that the base Image does not apply an index to upload_time, so if you want that, you must specify it.

## Auto-delete
### Overview
I read somewhere that a long time ago, Django would auto-delete files. This probably happened in model fields. This behaviour is not true now. If objects and fields are deleted, files are left in the host system. However, it suits this application, and some of it's intended uses, to auto-delete mod els and files. If you would like this behaviour, the app provides some solutions.

There are aspects to this. First, the files for Reforms are always deleted with the reform. And reforms are always deleted when the image model is deleted. However, the choices arrive with the deletion of the Image. Should the file be deleted with the Image?  Finally, should an Image be deleted when a model using that image is deleted?


#### Auto-delete of Reforms
Reform files are deleted with the reform. There is nothing to do.

Reforms are treated as objects generated automatically, so automatic deletion is not controversial. Reform models are deleted by the CASCADE in the foreign key, and so are the files.


#### Auto-delete Image files
Image file deletion is optional. To auto-delete, set the Image model attribute 'auto_delete_files=True'.


### Automatic deletion of image models when a supporting object is deleted
Place this in the ready() method of the application,

    from image.signals import register_image_delete_handler


    class NewsConfig(AppConfig):
        ...

        def ready(self):
            super().ready()
            from news_article.models import NewsArticle
            register_image_delete_handler(NewsArticle)

The image fields must be ImageOneToOneFields, and the field attribute must be 'auto_delete=True'.

#### Why must the code run on the custom field, and why not on a ImageOneToManyField?
The custom field means lightweight field identification.
 
An ImageOneToManyField implies an image pool. Many connections to one image. This is a  classic computing problem of reference counting. Best avoided.







### Behaviour of the default repository
By default, the default repository will not auto-delete the original files associated with Images. It will auto-delete reform models and their files.



## Filters
### Overview
Filters are used to describe how an uploaded image should be modified for display. In the background, the app will automatically adjust the image to the filter specification (or use a cached version).
 
A few filters are predefined. One utility/test filter,

<dl>
<dt>Thumb</dt>
    <dd>A 64x64 pixel square</dd>
</dl>

And some base filters, which you can configure. These are centre-anchored, 

- Crop
- Resize
- SmartCrop
- SmartResize

If you only need different image sizes, you only need to configure these. But if you want to pass some time with image-processing code, you can add filters to generate ''PuddingColour' and other effects.


### Filter placement and registration
Files of filter definitions can be placed in any app. Create a file called 'image_filters.py' and off you go.

If you would prefer to gather all filters in one place, define the settings to include,

    IMAGES = [
        {
            'SEARCH_MODULES': [
                        "siteName",
            ],
        },
    ]

Then put a file 'image_filters.py' in the 'sitename' directory. If you use a central file, you should namespace the filters,

    BlogPostLarge:
        width : 256
        height 256


### Filter declarations
All builtin filter bases accept these attributes,

- width
- height
- format

Most filter code demands 'width' and 'height', but 'format' is optional. Without a stated format, the image format stays as it was (unless another setting is in place). Formats accepted are conservative,

    bmp, gif, ico, jpg, png, rgb, tiff, webp 

which should be written as above (lowercase, and 'jpg', not 'jpeg'). So,

    from image import Resize, registry

    class MediumImage(Resize)
        width=260
        height=350
        format='png'
        #fill_color="Coral"
        #jpeg_quality=28
        # optional effects

    registry.register(MediumImage)


Crop and Resize can/often result in images narrower in one dimension. 

The Smart filters do a background fill in a chosen colour. By usung a fill, they can maintain aspect rattio, but return the requested size,

    from image import ResizeSmart, registry

    class MediumImage(ResizeSmart):
        width=260
        height=350
        format='jpg'
        fill_color="Coral"

    registry.register(MediumImage)

Fill color is defined however the image library handles it. Both Pillow and Wand can handle CSS style hex e.g. '#00FF00' (green), and HTML colour-names e.g. 'AliceWhite'.


### Registering filters
Filters need to be registered. Registration style is like ModelAdmin, templates etc. Registration is to 'image.registry' (this is how templatetags find them).

You can use an explicit declaration,

    from image import ResizeSmart, registry

    ...

    registry.register(single_or_list_of_filters)

Or use the decorator,

    from image import register, ResizeSmart

    @register()
    class MediumImage(ResizeSmart):
        width=260
        height=350
        format='jpg'
        fill_color="Coral"


### Wand filters
The base filters in the Wand filter set have more attributes available. The 'wand' code needs Wand to be installed on the host computer. Assuming that, you gain these effects,

    from image import filters_wand, register

    @register()
    class Medium(filters_wand.ResizeSmart):
        width=260
        height=350
        format='jpg'
        pop=False
        greyscale=False
        night=False
        warm=False
        strong=False
        no=False
        watermark='image/watermark.png'



If you enable more than one effect, they will chain, though you have no control over order.

I lost my way with the Wand effects. There is no 'blur', no 'rotate', no 'waves'. But there is,

<dl>
    <dt>pop</dt>
    <dd>
        Tightens leveling of black and white
    </dd>
    <dt>greyscale</dt>
    <dd>
        A fast imitation
    </dd>
    <dt>night</dt>
    <dd>
        Pretend the picture is from a movie
    </dd>
    <dt>warm</dt>
    <dd>
        A small shift in hue to compensate for a common photography white-balance issue. 
    </dd>
    <dt>strong</dt>
    <dd>
        Oversaturate image colors (like everyone does on the web). Unlike 'pop' this will not stress contrast so flatten blacks and whites. You may or may not prefer this. 
    </dd>
    <dt>no</dt>
    <dd>
        Draw a red cross over the image
    </dd>
    <dt>watermark</dt>
    <dd>Accepts a URL to a watermark image template.
    </dd>
</dl>

Watermark deserves some explanation. This does not draw on the image, as text metrics are tricky to handle. You configure a URL stub to an image, here's a builtin,

    watermark = 'image/watermark.png'

The URL is Django static-aware, but will pass untouched if you give it a web-scheme URL (like the URLs in Django Media).
 
The template is scaled to the image-to-be-watermarked, then composited over the main image by 'dissolve'. So the watermark is customisable, can be used on most sizes of image, and is usually readable since aspect ratio is preserved.

It is probably worth saying again that you can not change the parameters, so the strengths of these effects, without creating a new filter.


### Writing custom filter code
First bear in mind that Image uses fixed parameters. So your filter must work with fixed parameters across a broad range of uploaded images. I don't want anyone to dive into code, put in hours of work, then ask me how they can create an online image-editing app. Not going to happen.

However, while I can't make a case for 'waves' or 'pudding-colour' filters, I can see uses. For example, Wagtail CMS uses the OpenCV library to generate images that auto-focus on facial imagery (i.e. not centrally crop). There are uses for that.

Second, bear in mind that image editing is lunging into another world, rather like creating Django Forms without using models and classes. It will take time. But there is help available. Inherit from 'image.Filter'. You will need to provide a 'process' method, which takes an open Python File and returns a ByteBufferIO and a file extension.

If you want the filter to work with the Pillow or Wand libraries, you can inherit from the PillowMixin or WandMixin. These cover filehandling for those libraries. Then you can provide a 'modify' method, which alters then returns an image in the format of those libraries.

See the code for details.


### Why can filters not be chained or given parameters?
This app only enables creation of fixed filters intended for a broad range of images. You write a filter with parameters, the processing order is fixed, and it is set.

This is a deliberate decision. It makes life easy. If you want to produce a front-end that can adjust the filters, or chain them, that is another step. This is not that app.


## Admin
### Overview
Image ships with stock Django admin. However, this is not always suited to the app, it's intended or possible uses. So there are some additions.

The admin provided has an attitude about how to use the app. It assumes that each model instance is locked to one file. If a model exists, then the file exists. If the admin is given the same file, it duplicates the file and model.

In this system, models that refer to Image models can be null and blank, which represents 'image not yet uploaded'. And it is possible to build systems that reuse images. It is the Image_instance->file connection that is locked.


### Package solutions
#### ImageCoreAdmin
For administration and maintenance of image collections. This is a specialised use, which would only be visible to end users if trusted.

Significant changes from stock admin,

- changelist is tidier and includes 'view' and 'delete' links
- changelist has searchable filenames
- change form has 'readonly' file data


##### Remove ImageCoreAdmin from central repository
Want Django stock admin? Change the comments in 'image/admin.py' from,

    # Custom admin interface disallows deletion of files from models.
    class ImageAdmin(ImageCoreAdmin):
        
    # Stock admin interface.
    #class ImageAdmin(admin.ModelAdmin):
        pass
            
            
    admin.site.register(Image, ImageAdmin)

to,

    # Custom admin interface disalows deletion of files from models.
    #class ImageAdmin(ImageCoreAdmin):
        
    # Stock admin interface.
    class ImageAdmin(admin.ModelAdmin):
        pass
        
        
    admin.site.register(Image, ImageAdmin)



##### Notes and alternatives for the core admin
You may provide no core admin at all. You can use the './manage.py' commands to do maintenance. The stock admin is provided to get you started.

If you prefer your own core admin, have a look at the code for ImageCoreAdmin in '/image/admins.py'. It provides some clues about how to do formfield overrides and other customisation.

You may find it more maintainable to duplicate and modify the admin code, rather than import and override.


#### LinkedImageAdmin
For administration of models that contain foreign key links to images.

This is a small override that should not interfere with other admin code. It disallows image editing once an image has been connected to a field (by upload or selection). e.g.

    from image.addmins import LinkedImageAdmin

        class NewsArticleAdmin(LinkedImageAdmin, admin.ModelAdmin):
            pass
            
            
        admin.site.register(NewsArticle, NewsArticleAdmin)



## Forms
### Overview
There's nothing special about using this app in forms. Even the custom fields are mostly renames, and create namespaces for custom admin configurations.

That said, the fields used internally are not standard. 

### ImageFileField
If you are interested in the internals, this does a few extra jobs beyond an ImageFile,

<dl>
    <dt>Contains extra config attributes,</dt>
    <dd>Most of which are gathered from the class configuration (e.g. max_upload size). The class can deconstruct these for migrations.</dd>
    <dt>extra validators<ddt>
    <dd>Beyond the standard Django field, this field and it's formfield actively check filesizes and extensions. Calls to is_valid() will run these validations.</dd>
</dl>

### For references to images
When images are referenced from another model, this would usually [use a Foreign Key on the referring model](#model-fields). 


## Template Tags
### Overview
For most uses, the app has only one template tag. There is another, for testing and edge cases.

### The 'image' tag
Let's say there is a filter named ''Large'. Add this to template code,

    {% load img_tags %}

    {% image report.img my_app.Large %}
 
then visit the page. The app will generate a ''Large' reform of 'report.image', to the spec given in the filter.

The tag can guess the app from the context. So,

     {% image report.img Large %}

Will assume the filter is in the app the context says the view comes from.

The tag accepts keyword parameters which become HTML attributes,

     {% image report.img Large class="report-image" %}

This renders similar to,

    <img src="/media/reforms/eoy-report_large.png" alt="eoy-report image" class="report-image">


### The 'query' tag
There is a tag to find images by a database query. Sometimes this will be useful, for fixed or temporary decoration/banners etc. It must be given the app/model path in full,

        {{ imagequery some_app_name.some_image_model_name "some_query" image.Large  }}

e.g.

        {{ imagequery image.Image "pk=1" image.Large  }}

or,

        {{ imagequery "src="taunton-skyscraper"" image.Large  }}

While this may be useful, especially for fixed logos or banners, if you are passing a model through a context it is unnecessary. 


### Filters from other apps
You can borrow filter collections from other apps. Use the module path and filter classname,

    {% image "urban_decay" different_app.filter_name  %} 

But try not to create a tangle between your apps. You would not do that with CSS or other similar resources. Store general filters in a central location, and namespace them.



## Management Commands
They are,

- image_create_bulk
- image_sync
- image_list
- reform_delete

All management commands can be pointed at subclasses of Image and Reform, as well as the default app models.

They do what they say. 'image_sync' is particularly useful, it will attempt to make models for orphaned files, or delete orphaned files, or delete models with missing files. These commands are useful for dev, too.





## Settings
### Overview
Image accepts settings in several places. The app has moved away from site-wide settings towards other placements. Here is a summary, in order of last placement wins,

### Image
<dl>
    <dt>reform_model</dt>
    <dd>
        default=AbstractReform
    </dd>
    <dt>upload_dir</dt>
    <dd>
        default='originals'
    </dd>
    <dt>filepath_length</dt>
    <dd>
        default=100
    </dd>
    <dt>form_limit_filepath_length</dt>
    <dd>
        default=True
    </dd>
    <dt>accept_formats</dt>
    <dd>
        default=None
    </dd>
    <dt>max_upload_size</dt>
    <dd>
        default=2MB
    </dd>
    <dt>auto_delete_files</dt>
    <dd>
        (if the Image is deleted, the file is deleted too) default=False  
    </dd>
</dl>

### Reform
<dl>
    <dt>upload_dir</dt>
    <dd>
        default='reforms'
    </dd>
    <dt>image_model</dt>
    <dd>
        default='image.Image'
    </dd>
    <dt>file_format</dt>
    <dd>
        (set the default format of reforms) default=original format, Reform attribute, filter attribute
    </dd>
    <dt>jpeg_quality</dt>
    <dd>
        (set the quality of JPEG reforms) default=80, Reform attribute, filter attribute
    </dd>
</dl>

### ImageOneToOneField
<dl>
    <dt>auto_delete</dt>
    <dd>
        if True, and signals are enabled, deletion of the model will delete image models.
    </dd>
</dl>
(the field naturally has many other settings, this setting is the only one related to this app)

### Site-wide settings
Images accepts some site-wide settings,

    IMAGES = [
        {
            'BROKEN': 'myapp/lonely.png',
            'SEARCH_APP_DIRS': True,
            'SEARCH_MODULES': [
                        "someSiteName",
            ],
        },
    ]

<dl>
    <dt>BROKEN</dt>
    <dd>
    URL of a static file displayed in place of unreadable files. Takes a static-aware URL to a file. URLs with a web-based scheme pass untouched, relative URLs are assumed in an app's static folder. Default is 'image/unfound.png'.
    </dd>
    <dt>SEARCH_APP_DIRS</dt>
    <dd>
    Find 'image_filters.py' files in apps. If False, the app only uses filters defined in the core app and SEARCH_MODULES setting.
    </dd>
    <dt>SEARCH_MODULES</dt>
    <dd>
    Defines extra places to find 'image_filter.py' files. The above example suggests a site-wide filter collection in the site directory (most page-based Django sites have central collections of templates and CSS in the same directory). The setting takes module paths, not filepaths, because 'image_filter.py' files are live code.
    </dd>
</dl>



## Broken Images
The app throws a special error if images are broken i.e. files are missing or unreadable. In this case a stock 'broken' image is returned. Using the standard tags there is no need to configure or change in any way for this. The image can be [redefined](#site-wide-settings).


    
        
## Utilities
### The View
Image has a builtin template for a view. It's main purpose is to test filter code. As a test and trial device, it is not enabled by default.

Make a view,

    from django.views.generic import DetailView
    from NewsArticleImage.models import NewsArticleImage

    class NewsArticleImageDetailView(DetailView):
        template_name='image/image_detail.html'
        model = NewsArticleImage
        context_object_name = 'image'

Goto urls.py, add this,

    from test_image.views import NewsArticleImageDetailView

    path('newsarticleimage/<int:pk>/', NewsArticleImageDetailView.as_view(), name='news-article-image-detail'),

Now visit (probably),

    http://localhost:8000/image/1/

In the template you can edit the tag to point at your own configurations. With visible results and basic image data, the view is often easier to use than the shell.


## Tests
I've not found a way to test this app without Python ducktape. There are tests. They are in a directory 'test_image'. This is a full app.

To run the tests you must install django-img, then move 'test_image' to the top level of a project. Install,

        INSTALLED_APPS = [
            ...
            'test_image.apps.TestImageConfig',
            'image.apps.ImageConfig',
            ...
        ]

...and migrate. The tests are in the ''tests' sub-folder of 'test_image'.


## Notes
No SVG support: would require shadow code, Pillow especially can't handle them.

Widths, heights and bytesize of original images are recorded: in case the storage media is not local files but cloud provision.

The app generally uses URLs, not the filepaths: this can be confusing, but means the app is 'static' aware, and it should keep working if you swap storage backends.


## Credits
This is a rewrite of the Image app from Wagtail CMS. Some core ideas are from Wagtail, such as the broken image handling and replicable repositories. Some patches of code are also similar, or only lightly modified, such as the upload and storage code. However, the configuration options and actions have been changed, and the filtering actions are entirely new.

[Wagtail documentation](https://docs.wagtail.io/en/v2.8.1/advanced_topics/images/index.html)

