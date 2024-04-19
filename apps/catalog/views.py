import requests
from django.urls import reverse

from apps.main.mixins import ListViewBreadcrumbMixin, DetailViewBreadcrumbMixin
from .models import Catalog, Product, CategoryDTO, ProductDTO


# import Q

# Create your views here.

class CataloglistView(ListViewBreadcrumbMixin):
    model = Catalog
    template_name = 'catalog/index.html'
    context_object_name = 'categories'

    def get_new_offers(self):
        url = 'https://prod.salesbox.me/api/v4/companies/barnipet/offers/get-new-offers?lang=uk'
        response = requests.get(url)
        products = response.json()['data']
        dtos = []
        for product in products:
            dtos.append(ProductDTO.from_dict(product))
        return dtos

    def get_queryset(self):
        return Catalog.objects.order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offers'] = self.get_new_offers()
        return context

    def get_breradcrumb(self):
        self.breadcrumbs = {
            'current': 'Каталог',
        }
        return self.breadcrumbs


class ProductByCategoryView(ListViewBreadcrumbMixin):
    model = Catalog
    template_name = 'catalog/product_by_category.html'
    context_object_name = 'category'

    def get_product_list(self, categoryId, internalCategoryId):
        # url = 'https://prod.salesbox.me/api/v4/companies/barnipet/offers/filter?page=1&pageSize=20&categoryId={}'.format(categoryId)
        url = f'https://prod.salesbox.me/api/v4/companies/barnipet/offers/filter?page=1&pageSize=20&categoryInternalId={internalCategoryId}&categoryId={categoryId}&lang=uk'
        response = requests.get(url)
        data = response.json()
        return data

    def get_current_category(self, categoryId):
        model = Catalog.objects.get(id=categoryId)
        return CategoryDTO.from_dict(model.__dict__)

    def getCategories(self):
        categories = []
        for category in Catalog.objects.order_by("order"):
            categories.append(CategoryDTO.from_dict(category.__dict__))
        return categories


    def get_queryset(self):
        categoryId = self.kwargs['category_id']
        self.categories = self.getCategories()
        self.category = self.get_current_category(categoryId)
        products = self.get_product_list(categoryId, self.category.get_internal_id())['data']
        dtos = []
        for product in products:
            dtos.append(ProductDTO.from_dict(product))

        print(products)
        return dtos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = self.categories
        context['category'] = self.category
        return context

    def get_breradcrumb(self):
        self.breadcrumbs = {
            'current': self.category.name,
        }
        return self.breadcrumbs



class ProductDetailView(DetailViewBreadcrumbMixin):
    model = Product
    template_name = 'catalog/product.html'
    context_object_name = 'product'
    
    def get_breradcrumb(self):
        breadcrumbs = { reverse('catalog:index'): 'Каталог' }
        category = self.object.main_category()
        if category:
            if category.parent:
                linkss = []
                parent = category.parent
                while parent is not None:
                    linkss.append(
                        (
                            reverse('catalog:category', kwargs={'slug': parent.slug}),
                            parent.name
                        )
                    )
                    parent = parent.parent
                for url, name in reversed(linkss):
                    breadcrumbs[url] = name
                    breadcrumbs.update({url: name})
            breadcrumbs.update({reverse('catalog:category', kwargs={'slug': category.slug}): category.name})
        breadcrumbs.update({'current': self.object.name})
        return breadcrumbs







