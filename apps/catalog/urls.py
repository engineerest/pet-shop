from django.urls import path

from .views import CataloglistView, ProductByCategoryView, ProductDetailView, CartListView

app_name = 'catalog'

urlpatterns = [
    path('', CataloglistView.as_view(), name='index'),
    path('cart_page', CartListView.as_view(), name='cart_page'),
    path('<str:category_id>', ProductByCategoryView.as_view() , name='category'),
    path('products/<str:product_id>', ProductDetailView.as_view(), name='product'),
]