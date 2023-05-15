from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Address, Category, Product, Cart, Order, Tag, UserProfile, Favorites, UserTag, CustomUser

# Register your models here.
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'locality', 'city', 'state')
    list_filter = ('city', 'state')
    list_per_page = 10
    search_fields = ('locality', 'city', 'state')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category_image', 'is_active', 'is_featured', 'updated_at')
    list_editable = ('slug', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured')
    list_per_page = 10
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title", )}


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'product_image', 'is_active', 'is_featured', 'updated_at', 'display_tags')
    list_editable = ('slug', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured')
    list_per_page = 20
    search_fields = ('title', 'category__title', 'short_description')
    filter_horizontal = ('category',)
    prepopulated_fields = {"slug": ("title", )}
    
    def display_tags(self, obj):
        return ", ".join([tag.tag for tag in obj.tags.all()])
    display_tags.short_description = "Tags"

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at')
    list_editable = ('quantity',)
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('user', 'product')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'status', 'ordered_date')
    list_editable = ('quantity', 'status')
    list_filter = ('status', 'ordered_date')
    list_per_page = 20
    search_fields = ('user', 'product')

class TagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'info', 'created_at', 'updated_at')
    list_editable = ('info',)
    list_per_page = 10
    search_fields = ('tag', 'info')
    list_display_links = ('tag',)



class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'user profiles'

class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )
    def tags(self, instance):
        return ", ".join([tag.tag for tag in instance.userprofile.tags.all()])
    list_display = UserAdmin.list_display + ('tags',)



# Define un formulario para agregar tags a un producto en línea.
class ProductTagInline(admin.TabularInline):
    model = Product.tags.through
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    # otros atributos del modelo admin
    inlines = [ProductTagInline,]




class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'product',  'created_at')
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('user', 'product')


class UserTagAdmin(admin.ModelAdmin):
    list_display = ('user', 'tag', 'created_at')
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('user', 'tag')


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_user_tags')
    list_filter = ('user', 'user_tags')
    list_per_page = 20
    search_fields = ('user', 'user_tags__tag')  # Utiliza user_tags__tag para buscar en el campo 'tag' de la relación ManyToMany

    def display_user_tags(self, obj):
        return ', '.join(tag.tag for tag in obj.user_tags.all())
    display_user_tags.short_description = 'User Tags'


admin.site.register(Address, AddressAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorites, FavoritesAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserTag, UserTagAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
