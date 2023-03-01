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
                path('adminOrderView',views.adminOrderView,name='adminOrderView'),  
                path('singleOrderView',views.singleOrderView,name='singleOrderView'),  
                path('singleOrderEdit',views.singleOrderEdit,name='singleOrderEdit'),  
                path('userView',views.userView,name='userView'),  
                path('singleUserView',views.singleUserView,name='singleUserView'),  
                path('userBlock',views.userBlock,name='userBlock'),  
                path('addUser',views.addUser,name='addUser'),  
                path('getProductList',views.getProductList,name='getProductList'),  
                path('updateAddedProducts',views.updateAddedProducts,name='updateAddedProducts'),  
                path('updateAddedProductsQuantity',views.updateAddedProductsQuantity,name='updateAddedProductsQuantity'),  
                path('updateAddedProductsDelete',views.updateAddedProductsDelete,name='updateAddedProductsDelete'),  
                path('orderUserDetails',views.orderUserDetails,name='orderUserDetails'),  
                path('adminStartPayment',views.adminStartPayment,name='adminStartPayment'),  
                path('adminHandlePaymentSuccess',views.adminHandlePaymentSuccess,name='adminHandlePaymentSuccess'),  
                path('adminOrderMarkAsPaid',views.adminOrderMarkAsPaid,name='adminOrderMarkAsPaid'),  
              ]+static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)