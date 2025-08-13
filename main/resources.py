from import_export import resources
from main.models import Product


class ProductResource(resources.ModelResource):

    class Meta:
        model = Product
        export_order = ('code', 'category', 'name', 'active_ingredient')
        fields = ('code', 'category', 'name', 'active_ingredient', 'presentation', 'unit_price', 'unit_price_tops',
                  'unit_price_farma', 'unit_price_mayoristas', 'unit_price_institutions')
        import_id_fields = ['code']
        skip_unchanged = True
        use_bulk = True
