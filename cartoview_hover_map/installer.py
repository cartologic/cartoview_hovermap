from django.contrib.contenttypes.models import ContentType

info = {
    "title": "Hover Map",
    "description": "Select your map to be a hovering map",
    "author": 'Cartologic',
    "tags": ['Maps'],
    "licence": 'BSD',
    "author_website": "http://www.cartologic.com",
    "single_instance": False
}

def install():
    pass

def uninstall():
    ContentType.objects.filter(app_label="APP_NAME").delete();