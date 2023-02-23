from django.urls import path
import admin_realvedic_app.views as views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                path('login',views.login,name='login'),
                path('adminProductView',views.adminProductView,name='adminProductView'),
                path('adminProductDelete',views.adminProductDelete,name='adminProductDelete'),
                path('singleProductView',views.singleProductView,name='singleProductView'),
                path('siblingProductList',views.siblingProductList,name='siblingProductList'),
                path('singleProductEdit',views.singleProductEdit,name='singleProductEdit'),
                path('storeImage',views.storeImage,name='storeImage'),
                path('addNewProduct',views.addNewProduct,name='addNewProduct'),
                
                
              ]+static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)