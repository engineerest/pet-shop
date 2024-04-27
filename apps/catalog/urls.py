from django.urls import path

from . import views
from .views import CataloglistView, ProductByCategoryView, ProductDetailView, CartListView

app_name = 'catalog'

urlpatterns = [
    path('', CataloglistView.as_view(), name='index'),
    path('cart', CartListView.as_view(), name='cart'),
    path('<str:product_id>/add/', ProductByCategoryView.addToCart, name='add'),
    path('<str:category_id>', ProductByCategoryView.as_view() , name='category'),
    path('products/<str:product_id>', ProductDetailView.as_view(), name='product'),
    path('<str:cart_id>/order/<str:order_id>/increment/', CartListView.increment, name='increment'),
    path('<str:cart_id>/order/<str:order_id>/decrement/', CartListView.decrement, name='decrement'),
    path('<str:cart_id>/order/<str:order_id>/delete/', CartListView.deleteOrder, name='delete')
]