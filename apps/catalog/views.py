from datetime import timezone, datetime
from multiprocessing import context
from os import path

import requests
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.main.mixins import ListViewBreadcrumbMixin, DetailViewBreadcrumbMixin
from .models import Catalog, Product, CategoryDTO, ProductDTO, Cart, Order


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
    def get_product_by_id(productId):
        url = f'https://prod.salesbox.me/api/v4/companies/barnipet/offers/{productId}'
        response = requests.get(url)
        payload = response.json()['data']
        return ProductDTO.from_dict(payload)

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

    def addToCart(request, product_id):
        session_id = request.session.session_key
        print(session_id)

        if session_id is None:
            raise Exception("No active session")
        cart = None
        try:
            cart = Cart.objects.get(id=session_id)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(id=session_id)

        try:
            order_query = Order.objects.get(productId=product_id, cart=cart)
            order = order_query.__dict__
            order_id = order['id']
            quantity = order['quantity']
            Order.objects.filter(id=order_id).update(quantity=quantity + 1, updated=datetime.now())
        except Order.DoesNotExist:
            orderDTO = ProductByCategoryView.get_product_by_id(productId=product_id)
            order = Order(productId=product_id, name=orderDTO.name, price=orderDTO.price, previewURL=orderDTO.previewURL, quantity=1, created=datetime.now(), updated=datetime.now(), cart=cart)
            Order.save(order)
        return HttpResponseRedirect("catalog")

class ProductDetailView(ListViewBreadcrumbMixin):
    model = Product
    template_name = 'catalog/product.html'
    context_object_name = 'product'
    
    def get_breradcrumb(self):
        breadcrumbs = { reverse('catalog:index'): 'Каталог' }
        return breadcrumbs

    def get_product_by_id(self, product_id):
        url = f'https://prod.salesbox.me/api/v4/companies/barnipet/offers/{product_id}?lang=uk'
        response = requests.get(url)
        data = response.json()['data']
        if data is not None:
            return ProductDTO.from_dict(data)
        return None
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.get_product_by_id(self.kwargs['product_id'])
        return context


class CartListView(ListViewBreadcrumbMixin):
    # model = Cart
    template_name = 'catalog/cart.html'
    context_object_name = 'cart'

    def get_queryset(self):
        return self.find_of_create_cart()

    def get_breradcrumb(self):
        breadcrumbs = {reverse('catalog:index'): 'Каталог'}
        return breadcrumbs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.find_of_create_cart()
        context['cart'] = cart

        orders = Order.objects.filter(cart=cart)
        context['orders'] = orders

        total = 0
        for order in orders:
            total += order.get_cost()

        context['total'] = total
        return context

    def find_of_create_cart(self):
        session_id = self.request.session.session_key
        print(session_id)

        if session_id is None:
            raise Exception("No active session")

        try:
            return Cart.objects.get(id=session_id)
        except Cart.DoesNotExist:
            print("cart does not exist")
            print("Creating new cart")
            return Cart.objects.create(id=session_id)

    def decrement(request, cart_id, order_id):
        quantity = Order.objects.get(id=order_id).__dict__['quantity']
        if quantity == 1:
            Order.objects.get(id=order_id).delete()
        else:
            Order.objects.filter(id=order_id).update(quantity=quantity - 1)

        return HttpResponseRedirect("/catalog/cart")

    def increment(request, cart_id, order_id):
        quantity = Order.objects.get(id=order_id).__dict__['quantity']
        Order.objects.filter(id=order_id).update(quantity=quantity + 1)

        return HttpResponseRedirect("/catalog/cart")

    def deleteOrder(request, cart_id, order_id):
        order = Order.objects.get(id=order_id)
        order.delete()
        return HttpResponseRedirect("/catalog/cart")


    # return HttpResponseRedirect("/catalog/cart")