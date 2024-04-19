import uuid

from django.contrib.admin import display
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFill


# Create your models here.
class Catalog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    internalId = models.TextField(blank=True, verbose_name='Внутрішній ід', null=True)
    name = models.CharField(max_length=255, verbose_name='Назва')
    description = models.TextField(blank=True, verbose_name='Опис', null=True)
    baseUrl = models.TextField(blank=True, verbose_name='Джерело', null=True)
    originalURL = models.TextField(blank=True, verbose_name='Зображення', null=True)
    previewURL = models.TextField(blank=True, verbose_name='Іконка', null=True)
    order = models.IntegerField(verbose_name='Порядок', default=0)

    def get_absolute_url(self):
        return '/catalog/{}'.format(self.id)

    def has_image(self):
        return self.previewURL is not None

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['name']
        
        
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='Назва')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Опис', null=True)
    quantity = models.PositiveIntegerField(verbose_name='Кількість', default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ціна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')
    category = models.ManyToManyField(
        to=Catalog,
        related_name='products',
        through='ProductCategory',
        verbose_name='Категорії',
        blank=True,
    )
    
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['-created_at']
        
        
    def __str__(self):
        return self.name
    
    
    
    
    
    def get_absolute_url(self):
        return reverse("catalog:product", kwargs={"category_slug": self.main_category().slug, "slug": self.slug})

    def all_images(self):
        return Image.objects.filter(product=self.id)

    def main_image(self):
        image = Image.objects.filter(product=self.id, is_main=True).first()
        if image:
            return image
        return self.all_images().first()

    def main_category(self):
        category = self.category.filter(productcategory__is_main=True).first()
        print(category)
        if category:
            return category
        return self.category.first()


    @display(description='Ціна')
    def price_display(self):
        return f'{self.price} грн.'

    @display(description='Основне зображення')
    def image_tag(self):
        image = self.main_image()
        if image:
            return mark_safe(f'<img src="{image.image_thumbnail.url}" />')
    
    

class ProductCategory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    category = models.ForeignKey(Catalog, on_delete=models.CASCADE, verbose_name='Категорія')
    is_main = models.BooleanField(default=False, verbose_name='Основна категорія')
    
    def __str__(self):
        return f'{self.product.name} -> {self.category.name}'
    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.is_main:
            ProductCategory.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(force_insert, force_update, using, update_fields)
        
    class Meta:
        verbose_name = 'Категорія товару'
        verbose_name_plural = 'Категорії товарів'
        
        
class Image(models.Model):
    image = ProcessedImageField(
        verbose_name='Зображення',
        upload_to='catalog/products/',
        processors=[],
        format='JPEG',
        options={'quality': 100},
        blank=True,
        null=True
    )
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 200)],
        format='JPEG',
        options={'quality': 60}
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Товар'
    )
    is_main = models.BooleanField(default=False, verbose_name='Основне зображення')
    
    
    @display(description='Зображення')
    def image_tag_thumbnail(self):
        if self.image:
            return mark_safe(f'<img src="{self.image_thumbnail.url}" height="70" />')
        
    @display(description='Основне зображення')
    def image_tag(self):
        if self.image:
            return mark_safe(f'<img src="{self.image_thumbnail.url}" />')


class CategoryDTO:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.internalId = kwargs.get('internalId', None)
        self.name = kwargs.get('name', None)
        self.description = kwargs.get('description', None)
        self.baseUrl = kwargs.get('baseUrl', None)
        self.previewURL = kwargs.get('previewURL', None)
        self.originalURL = kwargs.get('originalURL', None)
        self.order = kwargs.get('order', None)

    def to_dict(self):
        return self.__dict__

    def get_absolute_url(self):
        return '/catalog/{}'.format(self.id)

    def get_internal_id(self):
        return self.internalId


    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class ProductDTO:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.internalId = kwargs.get('internalId', None)
        self.previewURL = kwargs.get('previewURL', None)
        self.originalURL = kwargs.get('originalURL', None)
        self.price = kwargs.get('price', None)
        self.names = kwargs.get('names', None)
        self.name = kwargs.get('name', None)

    def to_dict(self):
        return self.__dict__

    def get_absolute_url(self):
        return '/products/{}'.format(self.id)

    def get_name(self):
        if self.name is not None:
            return self.name
        self.name = 'Якась фігня'
        for n in self.names:
            if n['lang'] == 'uk':
                name = n['name']
                break
        return name

    def has_image(self):
        return self.previewURL is not None



    @classmethod
    def from_dict(cls, data):
        return cls(**data)
