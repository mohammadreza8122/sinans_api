
from category.models import Category
import json
from django.conf import settings
from category.models import Category
import json

from service.models import HomeCareCategory, HomeCareService

with open(f'{settings.BASE_DIR}/category/categories_hierarchy.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


def add_categories(category_data, parent=None):
    if parent is None:
        category = Category.add_root(title=category_data['title'], slug=category_data['slug'])
    else:
        category = parent.add_child(title=category_data['title'], slug=category_data['slug'])

    for child in category_data.get('children', []):
        add_categories(child, category)



def add_meta():
    sc = HomeCareCategory.objects.all()
    for c in sc:
        cat = Category.objects.filter(slug=c.slug).first()
        if cat:
            print(c.image)
            print(c.meta_keywords)
            cat.meta_description = c.meta_description
            cat.meta_keywords = c.meta_keywords
            cat.image = c.image
            cat.save()


def add_service():
    services = HomeCareService.objects.all()
    for ser in services:
        if ser.category:
            cat = Category.objects.filter(slug=ser.category.slug).first()
            if not cat:
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!           ', ser.pk )
            ser.category_new = cat
            ser.save()
        else:
            print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&        ', ser.pk)


# دستگاه فشارسنج زیر دسته دستگاه فشارسنج
# فشار سنج مچی زیر دسته دستگاه فشارسنج
# SERVICE ======>>>>>>>>>>> فشارسنج مچی دیجیتال 735 زنیت مد      959




# add_service()
#
# for d in data:
#     print(d)
#     add_categories(d)
