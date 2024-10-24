
from category.models import Category
import json
from django.conf import settings
with open(f'{settings.BASE_DIR}/category/categories_hierarchy.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def bad(data):
    Category.objects.all().delete()
    for d in data:
        print(d)
        category = Category.add_root(title=d['title'], slug=d['slug'])
        if d['children']:
            for c in d['children']:
                c_category= category.add_child(title=c['title'], slug=c['slug'])

                if c['children']:
                    for b in c['children']:
                        b_category = c_category.add_child(title=b['title'], slug=b['slug'])

                        if b['children']:
                            for f in b['children']:
                                f_category = b_category.add_child(title=f['title'], slug=f['slug'])

                                if f['children']:
                                    for o in f['children']:
                                        o_category = f_category.add_child(title=o['title'], slug=o['slug'])

                                        if o['children']:
                                            for p in o['children']:
                                                p_category = o_category.add_child(title=p['title'], slug=p['slug'])

                                                if p['children']:
                                                    for j in p['children']:
                                                        j_category = p_category.add_child(title=j['title'], slug=j['slug'])

                                                        if j['children']:
                                                            for l in j['children']:
                                                                l_category = j_category.add_child(title=l['title'],
                                                                                                  slug=l['slug'])

                                                                if l['children']:
                                                                    for r in l['children']:
                                                                        r_category = l_category.add_child(title=r['title'],
                                                                                                          slug=r['slug'])



Category.objects.all().delete()
from category.models import Category
import json

def add_categories(category_data, parent=None):
    if parent is None:
        category = Category.add_root(title=category_data['title'], slug=category_data['slug'])
    else:
        category = parent.add_child(title=category_data['title'], slug=category_data['slug'])

    for child in category_data.get('children', []):
        add_categories(child, category)




for d in data:
    print(d)
    add_categories(d)



