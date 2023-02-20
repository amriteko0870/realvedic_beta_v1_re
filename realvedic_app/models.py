from django.db import models

# Create your models here.
class customer_details(models.Model):
    customer_id = models.TextField()
    customer_name = models.TextField()
    email = models.TextField()
    contact = models.TextField()
    Address_line1 = models.TextField()
    Address_line2 = models.TextField()
    city = models.TextField()
    pincode = models.TextField()
    state = models.TextField()
    Country = models.TextField()
    
class Product_data(models.Model):
    
    title = models.TextField(blank = True)
    category = models.TextField(blank = True)
    about = models.TextField(blank = True)
    image = models.TextField(blank=True)
    price = models.TextField(blank = True)
    discount = models.TextField(blank=True)
    size = models.TextField(blank = True)
    benefits = models.TextField(blank = True)
    ingredients= models.TextField(blank = True)
    how_to_use=models.TextField(blank = True)
    how_we_make_it = models.TextField(blank = True)
    nutrition= models.TextField(blank = True)
    Status = models.TextField(blank = True)
    sibling_product=models.TextField(blank = True)
    HSN=models.TextField(blank = True)
    SKU=models.TextField(blank = True)
    tax = models.TextField()

class categoryy(models.Model):
    category=models.TextField()
    category_colour=models.TextField()
    category_image=models.TextField()
    category_banner=models.TextField()
    category_banner_mobile=models.TextField()
#-----------------------------------------------------------------------------------------------
order_status_choices=(
    ('placed','PLACED'),
    ("Processed",'processed'),
    ('dispatched','DISPATCHED',),
    ('on the way','On the way'),
    ('delivered','DELIVERED'),
    ('CANCELLED','cancelled'),
    ('RETURNED','returned'),

)
'''class order_data(models.Model):
    order_id=models.TextField()
    user_id = models.TextField(null=True,blank=True)
    placed_at = models.DateField(auto_now_add=True,blank=True,null=True)
    Product_id = models.TextField(null=True,blank=True)
    size = models.TextField(null=True,blank=True)
    price_per_unit=models.TextField(null=True,blank=True)
    quantity = models.TextField(null=True,blank=True)
    Total_amount = models.TextField(null=True,blank=True)
    status=models.CharField(max_length=50,choices = order_status_choices,default='Placed')
    image=models.TextField(blank=True,null=True)'''

class Order_data(models.Model):
    order_id=models.TextField()
    user_id = models.TextField(null=True,blank=True)
    placed_at = models.DateField(auto_now_add=True,blank=True,null=True)
    product_details=models.TextField(null=True,blank=True)
    Total_amount = models.TextField(null=True,blank=True)
    status=models.CharField(max_length=50,choices = order_status_choices,default='Placed')



class images_and_banners(models.Model):
    title=models.TextField()
    image=models.TextField()
    product_id = models.TextField(blank=True)

class blogs(models.Model):
    image=models.TextField()
    title=models.TextField()
    content=models.TextField()
    Points=models.TextField(blank=True)

#-------------------------------------------------user side models--------------------------------------

class user_cart(models.Model):
    user_id = models.TextField(blank=True)
    product_id = models.TextField()
    size = models.TextField()
    price_per_unit=models.TextField(blank=True)
    quantity = models.TextField(blank=False,default=0)
    image=models.TextField(blank=True,null=True)
    no_login_id = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class user_data(models.Model):
    first_name = models.TextField()
    last_name = models.TextField(blank=True)
    email = models.TextField()
    gender = models.TextField()
    dob = models.TextField()
    phone_code = models.TextField()
    phone_no = models.TextField()
    password = models.TextField()
    token = models.TextField()

class user_address(models.Model):
    user_id = models.TextField()
    add_line_1 = models.TextField(blank=True)
    add_line_2 = models.TextField(null=True,blank=True)
    landmark = models.TextField(null=True,blank=True)
    city = models.TextField(blank=True)
    state = models.TextField(blank=True)
    country = models.TextField(blank=True)
    pincode = models.TextField(blank=True)
    phone_no = models.TextField(blank=True)

class noLoginUser(models.Model):
    token = models.TextField(blank=True)


class PaymentOrder(models.Model):
    order_product = models.TextField()
    order_amount = models.TextField()
    order_payment_id = models.TextField()
    isPaid = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now=True)
    user_id=models.TextField(null=True)
    order_status = models.TextField(blank = True) #placed > processed > dispatched > on the way > delivered


class doctor_info(models.Model):
      title=models.TextField(blank=True) 
      education=models.TextField(blank=True)
      experience=models.TextField(blank=True)
      speciality=models.TextField(blank=True)
      available=models.TextField(blank=True)
      image=models.TextField()










