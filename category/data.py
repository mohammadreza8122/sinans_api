from unicodedata import category

from django.template.defaultfilters import first

from category.models import Category
import json
from django.conf import settings
from category.models import Category
import json
from django.db.models import Q
from service.models import HomeCareCategory, HomeCareService, HomeCareServicePrice

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








def get_five():
    category_1 = Category.get_root_nodes()
    category_list = []
    for c1 in category_1:
        category_list.append(c1)
        category_2 = c1.get_children()

        for c2 in category_2:
            category_list.append(c2)
            category_3 = c2.get_children()
            
            for c3 in category_3:
                category_list.append(c3)
                category_4 = c3.get_children()

                for c4 in category_4:
                    category_list.append(c4)
                

    print(category_list)
    return category_list



def add_city(cats):
    for cat in cats:
        city_list = []
        print('+++++++++++')
        child = cat.get_descendants()
        services = HomeCareService.objects.filter(Q(category_new=cat) |  Q(category_new__in=child))

        if services:
            s = HomeCareServicePrice.objects.filter(
                service__in=services
            )
            if s:
                for a in s:
                    if a.city:
                        if a.city.pk not in city_list:
                            city_list.append(a.city.pk)
        # print(set(city_list))
        print(city_list)
        cat.cites = {'city_list': city_list}
        cat.save()
        # city_list = []



def add_company(cats):
    for cat in cats:
        company_list = []

        print('+++++++++++')
        child = cat.get_descendants()
        services = HomeCareService.objects.filter(Q(category_new=cat) | Q(category_new__in=child))
        if services:
            s = HomeCareServicePrice.objects.filter(
                service__in=services
            )
            if s.exists():
                for c in s:
                    if c.company and c.company.id not in company_list:
                        company_list.append(c.company.pk)
        cat.company_list = {'company_list': company_list}
        cat.save()
        print(company_list)


def add_plus(cats):
    for cat in cats:
        company_list = []

        print('+++++++++++')
        child = cat.get_descendants()
        services = HomeCareService.objects.filter(Q(category_new=cat) | Q(category_new__in=child))
        if services:
            s = HomeCareServicePrice.objects.filter(
                service__in=services
            )
            if s.exists():
                for c in s:
                    if c.company and c.company.id not in company_list and c.company.is_plus:
                        company_list.append(c.company.pk)
        cat.company_list = {'plus_list': company_list}
        cat.save()
        print(company_list)


# cats = get_five()
# add_city(cats)
# add_company(cats)
# add_plus(cats)


# دستگاه فشارسنج زیر دسته دستگاه فشارسنج
# فشار سنج مچی زیر دسته دستگاه فشارسنج
# SERVICE ======>>>>>>>>>>> فشارسنج مچی دیجیتال 735 زنیت مد      959


# add_company()
# add_service()
#
# for d in data:
#     print(d)
#     add_categories(d)
