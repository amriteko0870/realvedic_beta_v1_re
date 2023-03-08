from django.contrib import admin
from realvedic_app.models import Product_data,categoryy,images_and_banners,blogs,user_data,user_cart,user_address,PaymentOrder,doctor_info,noLoginUser,shipping_price

# Register your models here.
#admin.site.register(Seller_details)
#admin.site.register(Product_data)
#admin.site.register(order_data)

admin.site.register(Product_data)
admin.site.register(categoryy)
admin.site.register(images_and_banners)
admin.site.register(blogs)
admin.site.register(user_data)
admin.site.register(user_cart)
admin.site.register(user_address)
admin.site.register(PaymentOrder)
admin.site.register(doctor_info)
admin.site.register(noLoginUser)
admin.site.register(shipping_price)

