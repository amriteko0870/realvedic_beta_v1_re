from django.urls import path
import realvedic_app.views as views 
import realvedic_app.test_code as t_views

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
                path('userAccountView',views.userAccountView,name='userAccountView'),
                path('UserAccountEdit',views.UserAccountEdit,name='UserAccountEdit'),
                # path('start_payment',views.start_payment,name='start_payment'),
                # path('handle_payment_success',views.handle_payment_success,name='handle_payment_success'),
                path('order_view',views.order_view,name='order_view'),
                path('single_order_view',views.single_order_view,name='single_order_view'),
                
                path('categoryPage2',t_views.categoryPage2,name='categoryPage2'),
                path('write_data2',t_views.landing_page2,name='landing_page2'),
                path('single_product_view2',t_views.single_product_view2,name='single_product_view2'),
                path('recently_viewed_oc',t_views.recently_viewed_oc,name='recently_viewed_oc'), 

                path('start_payment',views.start_payment,name='start_payment'), 
                path('payment_success',views.payment_success,name='payment_success'), 
                path('payment_cancel',views.payment_cancel,name='payment_cancel'), 


                path('brand_page',views.brand_page,name='brand_page'), 
              ]+static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
