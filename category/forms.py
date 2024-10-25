from category.models import Category
from treebeard.forms import movenodeform_factory



class CategoryAdminForm(movenodeform_factory(Category)):
    def __init__(self, *args, **kwargs):
        super(CategoryAdminForm, self).__init__(*args, **kwargs)
        self.fields['_ref_node_id'].choices =  [(None, 'دسته بندی اصلی')] + self.fields['_ref_node_id'].choices[1:]

        self.fields['_ref_node_id'].label = 'والد'

    def clean(self):
        self.cleaned_data['_position'] = 'sorted-child'

