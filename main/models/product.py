from django.db import models


class Product(models.Model):

    class CategoryChoices(models.TextChoices):
        LINEA_RX = 'Línea RX'
        LINEA_OTC = 'Línea OTC'
        LINEA_GX = 'Línea GX'
        PERSONAL_CARE = 'Personal Care'

    category = models.CharField(max_length=50, verbose_name="Categoría", choices=CategoryChoices.choices)
    name = models.CharField(max_length=150, verbose_name="Nombre")
    active_ingredient = models.CharField(max_length=150, verbose_name="Principio activo", null=True, blank=True)
    presentation = models.CharField(max_length=150, verbose_name="Presentación", null=True, blank=True)
    show_on_catalog = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización", null=True, blank=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        name = self.name
        if self.presentation is not None:
            name += " - " + self.presentation
        return name

    @classmethod
    def get_column_rename(cls):
        return {
            'CÓDIGO DIPHA': 'code',
            'LÍNEA': 'category',
            'PRODUCTO': 'name',
            'PRINCIPIO ACTIVO': 'active_ingredient',
            'PRESENTACIÓN': 'presentation',
            'VVF': 'unit_price',
            'PRECIO TOPS S/IGV': 'unit_price_tops',
            'PRECIO FARMA S/IGV': 'unit_price_farma',
            'PRECIO MAYORISTAS S/IGV': 'unit_price_mayoristas',
            'PRECIO INSTITUCIONES S/IGV': 'unit_price_institutions'
        }

    @classmethod
    def import_from_excel(cls, file):
        import pandas as pd
        from tablib import Dataset
        from main.resources import ProductResource
        df = pd.read_excel(file)

        rename_columns = cls.get_column_rename()

        df.rename(columns=rename_columns, inplace=True)

        # Call the Student Resource Model and make its instance
        product_resource = ProductResource()

        # Load the pandas dataframe into a tablib dataset
        dataset = Dataset().load(df)

        # Call the import_data hook and pass the tablib dataset
        result = product_resource.import_data(dataset, dry_run=True, raise_errors=True)
        if not result.has_errors():
            result = product_resource.import_data(dataset, dry_run=False)
            print(result.total_rows)
            return result
        else:
            raise Exception("Error al importar productos. " + str(result.row_errors()[0]))
