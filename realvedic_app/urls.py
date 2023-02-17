from django.urls import path
import realvedic_app.views as views 

from django.conf.urls.static import static
from django.conf import settings


from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
                path('write_data',views.landing_page,name='landing_page'),
                path('single_product_view',views.single_product_view,name='single_product_view'),
                path('categoryPage',views.categoryPage,name='categoryPage'),
                path('NavbarCategoryView',views.NavbarCategoryView,name='NavbarCategoryView'),
                path('search_bar',views.search_bar,name='search_bar'),
                path('add_to_cart',views.add_to_cart,name='add_to_cart'),
                path('UserCartView',views.UserCartView,name='UserCartView'),
                path('CartUpdate',views.CartUpdate,name='CartUpdate'),
                path('CartitemDelete',views.CartitemDelete,name='CartitemDelete'),
                path('login',views.login,name='login'),
                path('signUp',views.signUp,name='signUp'),
                path('checkout',views.checkout,name='checkout'),
              
              ]+static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
