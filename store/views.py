import django
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Order, Product, Favorites, Tag, UserTag
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator # for Class Based Views
from django.db.models import Q, Count
from .models import Product
from django.shortcuts import redirect



# Create your views here.
def search(request):
    query = request.GET.get('q')
    products = Product.objects.all()
    categories = Category.objects.filter(is_active=True)
    if query:
        products = Product.objects.filter(Q(title__icontains=query) | Q(short_description__icontains=query) | Q(detail_description__icontains=query))
    user = request.user
    favorites = []
    if user.is_authenticated:
        favorites = Product.objects.filter(favorites__user=user)
    context = {'products': products, 'categories':categories, 'favorites': favorites,}
    return render(request, 'store/search.html', context)

def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/index.html', context)


def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = []
    for categoria in product.category.all():
        related_products += Product.objects.exclude(id=product.id).filter(is_active=True, category__title=categoria.title)
    categories=product.category.all()
    favorites = []
    user = request.user
    if user.is_authenticated:
        favorites = Product.objects.filter(favorites__user=user)
    context = {
        'product': product,
        'related_products': related_products,
        'categories': categories,
        'favorites': favorites,

    }
    return render(request, 'store/detail.html', context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    categories = Category.objects.filter(is_active=True)
    favorites = []
    user = request.user
    if user.is_authenticated:
        favorites = Product.objects.filter(favorites__user=user)
    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'favorites': favorites,
    }
    return render(request, 'store/category_products.html', context)


# Authentication Starts Here

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, 'account/register.html', {'form': form})
        

@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()
    
    return redirect('store:cart')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(5)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount
        
    shipping_amount = round(amount*shipping_amount/100,2)
    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')


@login_required
def checkout(request):
    user = request.user
    address_id = request.GET.get('address')
    
    address = get_object_or_404(Address, id=address_id)
    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Order(user=user, address=address, product=c.product, quantity=c.quantity).save()
        # And Deleting from Cart
        c.delete()
    return redirect('store:orders')


@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})





def shop(request):
    return render(request, 'store/shop.html')





def test(request):
    return render(request, 'store/test.html')










@login_required
def favorites(request):
    user = request.user
    favorites_products = Favorites.objects.filter(user=user)

    context = {
        'favorites_products': favorites_products,
    }
    return render(request, 'store/favorites.html', context)


@login_required
def remove_favorite(request, product_id):
    if request.method == 'GET':
        f = get_object_or_404(Favorites, product_id=product_id)
        f.delete()
        messages.success(request, "Product removed from Favorites.")
    return redirect('store:favorites')

@login_required
def add_to_favorites(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Favorites or Not
    item_already_in_favorites = Favorites.objects.filter(product=product_id, user=user)
    if item_already_in_favorites:
        messages.success(request, "Product is already in Favorites.")
    else:
        Favorites(user=user, product=product).save()
    
    return redirect('store:favorites')
    
@login_required
def cuestionario(request):
    user = request.user
    if request.method == 'POST':
        # Obtener respuestas del formulario
        answer1 = request.POST.get('question1')
        answer2 = request.POST.get('question2')
        answer3 = request.POST.get('question3')
        answer4 = request.POST.get('question4')
        answer5 = request.POST.get('question5')
        answer6 = request.POST.get('question6')
        answer7 = request.POST.get('question7')
        answer8 = request.POST.get('question8')

        # Asignar tags según las respuestas
        tags = []
        if answer1 == 'Sí':
            tags.append('aire_libre')
        if answer2 == 'Sí':
            tags.append('musica')
        if answer3 == 'Desconectar':
            tags.append('desconectar')
        if answer4 == 'Sí':
            tags.append('diferente')
        if answer5 == 'Sí':
            tags.append('social')
        if answer6 == 'Sí':
            tags.append('comida_bebida')
        if answer7 == 'Sí':
            tags.append('cultura')
        if answer8 == 'Sí':
            tags.append('deporte')

        # Eliminar todos los tags existentes del usuario
        user.customuser.user_tags.clear()
        
        # Guardar los tags asignados al usuario
        user_tags = Tag.objects.filter(tag__in=tags)
        for tag in user_tags:
            UserTag.objects.get_or_create(user=user.customuser, tag=tag)
        
        # Redirigir al usuario a la página de recomendaciones
        return redirect('store:recomendaciones')

    return render(request, 'store/cuestionario.html')

@login_required
def recomendaciones(request):
    user = request.user
    user_tags = user.customuser.user_tags.all()

    # Obtener los productos que tienen al menos uno de los tags del usuario
    products = Product.objects.filter(tags__in=user_tags).distinct()

    # Anotar la cantidad de tags en común con el usuario
    products = products.annotate(common_tags=Count('tags', filter=Q(tags__in=user_tags)))

    # Ordenar los productos por la cantidad de tags en común en orden descendente
    products = products.order_by('-common_tags')

    favorites = products.filter(favorites__user=user)

    context = {'products': products, 'favorites': favorites}
    return render(request, 'store/recomendaciones.html', context)