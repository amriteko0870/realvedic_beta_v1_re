from import_statements import *

#Putting data into database

@api_view(['POST'])
def landing_page(request):
    data = request.data
    token = data['token']
    try:
        user_data.objects.get(token = token)
        user = user_data.objects.get(token = token)
        cart_product_ids = user_cart.objects.filter(user_id = user.id).values_list('product_id',flat=True)
    except:
        no_login_token = data['no_login_token']
        # print("no_login_token",no_login_token)
        no_login_id = noLoginUser.objects.filter(token = no_login_token).values_list('id',flat=True)
        # print("no_login_id",no_login_id)
        if len(no_login_id) > 0:
            cart_product_ids = user_cart.objects.filter(no_login_id = str(no_login_id[0])).values_list('product_id',flat=True)
            # print("cart_product_ids",cart_product_ids)
        else:           
            cart_product_ids = []
    
    res = {}
    category_obj = categoryy.objects.annotate(
                                                title = F('category'),
                                                image = F('category_image')
                                             )\
                                    .values('id','title','image')
    res['tab'] = list(category_obj)[::-1]
    res['banner'] = images_and_banners.objects.filter(title = 'banner').values()
    
    def singleImageGet(x):
        return x.split(',')[0]
    def splitPipe(x):
        return x.split('|')
    def cartStatusCheck(x):
        if str(x) in cart_product_ids:
            return True
        else:
            return False
    top_seller = Product_data.objects.values('id','image','title','size','price')
    top_seller = pd.DataFrame(top_seller)
    top_seller['image'] = top_seller['image'].apply(singleImageGet)
    top_seller['weight'] = top_seller['size'].apply(splitPipe)
    top_seller['price'] = top_seller['price'].apply(splitPipe)
    top_seller['cart_status'] = top_seller['id'].apply(cartStatusCheck)
    top_seller = top_seller[['id','image','title','weight','price','cart_status']].to_dict(orient='records')
    top_seller = list(top_seller)[::-1][:5]
    res['top_seller_products'] = top_seller

    small_crousel = Product_data.objects.annotate(
                                                    product_id = F('id')
                                                 )\
                                        .values('product_id','title','image')
    small_crousel = list(small_crousel)[::-1][:10]
    small_crousel = pd.DataFrame(small_crousel)
    small_crousel['image'] = small_crousel['image'].apply(singleImageGet)
    small_crousel = small_crousel.to_dict(orient='records')
    res['small_carousal_images'] = small_crousel

    large_crousel = images_and_banners.objects.filter(title__contains='large_carousal_images_')\
                                              .values('image','product_id')
    res['large_carousal_images'] = large_crousel

    single_product_details = {}
    video_data = images_and_banners.objects.filter(title="Make Best Dosa with us!")\
                                           .annotate(video = F('image'))\
                                           .values('title','video').last()
    single_product_details['video_data'] = video_data
    food = Product_data.objects.order_by('?').values('id','title','image','price','size').first()
    food = pd.DataFrame([food])
    food['image'] = food['image'].apply(singleImageGet)
    food['weight'] = food['size'].apply(splitPipe)
    food['price'] = food['price'].apply(splitPipe)
    food['cart_status'] = food['id'].apply(cartStatusCheck)
    food = food[['id','image','title','weight','price','cart_status']].to_dict(orient='records')
    food = food[-1]
    single_product_details['food'] = food
    blog = blogs.objects.annotate(
                                    points = F('Points')
                                 )\
                        .values('id','image','title','content','points').last()
    blog['points'] = eval(blog['points'])
    single_product_details['blog'] = blog
    res['single_product_details'] = single_product_details
    return Response(res)

@api_view(['POST'])
def single_product_view(request):
    product_id=request.data["prod_id"]
    product_info = Product_data.objects.filter(id = product_id).values().last()
    res = {}
    try:
        token = request.data['token']
        user = user_data.objects.get(token = token)
        cart_product_ids = user_cart.objects.filter(user_id = user.id,product_id=product_id).values_list('quantity',flat=True)
        if len(cart_product_ids) > 0:
            quantity = cart_product_ids[0]
            cart_status = True
        else:
            quantity = 0
            cart_status = False
    except:
        no_login_token = request.data['no_login_token']
        no_login_id = noLoginUser.objects.filter(token = no_login_token).values_list('id',flat=True)
        cart_product_ids = user_cart.objects.filter(no_login_id = no_login_id[0],product_id=product_id).values_list('quantity',flat=True)
        # print('cart_product_ids',cart_product_ids)
        if len(cart_product_ids) > 0:
            quantity = cart_product_ids[0]
            cart_status = True
        else:           
            quantity = 0
            cart_status = False
    product_details = {}
    product_details['id'] = product_info['id']
    product_details['title'] = product_info['title']
    product_details['description'] = product_info['about']
    product_details['original_price'] = product_info['price'].split('|')[0]
    product_details['offer_price'] = str(round((int(product_info['price'].split('|')[0]) * 100)/(100 + int(product_info['discount']))))
    product_details['images'] = product_info['image'].split(',')
    product_details['quantity'] = quantity
    product_details['cart_status'] = cart_status
    product_details['pack_size'] = pd.DataFrame(
                                                    {
                                                        'weight':product_info['size'].split('|'),
                                                        'price':product_info['price'].split('|'),
                                                        'offer_price': map(lambda x : str(round((int(x) * 100)/(100 + int(product_info['discount'])))),
                                                                           product_info['price'].split('|'))      
                                                    }
                                               ).to_dict(orient="records")
    res['product_details'] = product_details
    res['benefits'] = {'title':'Benefits','description':product_info['benefits']}
    res['ingredients'] = {'title':'Ingredients','description':product_info['ingredients']}
    res['how_to_use'] = {'title':'How to use','description':product_info['how_to_use']}
    res['how_we_make_it'] = {'title':'how we make it','description':product_info['how_we_make_it']}
    res['nutrition'] = {'title':'Nutritional Info per 100g (Approx)*'}
    res['nutrition']['values'] = pd.DataFrame(
                                                {
                                                    'title': ['Total Fat','Protien','Carbohydrate','Energy'],
                                                    'value': product_info['nutrition'].split('|')
                                                }
                                             ).to_dict(orient="records")
    return Response(res)

@api_view(['POST'])
def categoryPage(request):
    data = request.data
    category_id = data['category']
    category_obj = categoryy.objects.filter(id = category_id).values().last()
    res={}
    try:
        token = data['token']
        user = user_data.objects.get(token = token)
        cart_product_ids = user_cart.objects.filter(user_id = user.id).values_list('product_id',flat=True)
    except:
        no_login_token = data['no_login_token']
        # print("no_login_token",no_login_token)
        no_login_id = noLoginUser.objects.filter(token = no_login_token).values_list('id',flat=True)
        # print("no_login_id",no_login_id)
        if len(no_login_id) > 0:
            cart_product_ids = user_cart.objects.filter(no_login_id = str(no_login_id[0])).values_list('product_id',flat=True)
            # print("cart_product_ids",cart_product_ids)
        else:           
            cart_product_ids = []
    res['category'] = category_obj['category']
    res['category_banner'] = category_obj['category_banner']
    if category_obj['category'] == 'All Products':
        products = Product_data.objects.values('id','title','image','size','price')
    else:
        products = Product_data.objects.filter(category = category_id).values('id','title','image','size','price')
    
    def getSingleImage(x):
        return x.split(',')[0]
    def splitByPipe(x):
        return x.split('|')
    def cartStatusCheck(x):
        if str(x) in cart_product_ids:
            return True
        else:
            return False
    products = pd.DataFrame(products)
    products['image'] = products['image'].apply(getSingleImage)
    products['weight'] = products['size'].apply(splitByPipe)
    products['price'] = products['price'].apply(splitByPipe)
    products['cart_status'] = products['id'].apply(cartStatusCheck)
    products = products[['id','title','image','weight','price','cart_status',]].to_dict(orient="records")
    res['products'] = products
    return Response(res)


@api_view(['GET'])
def NavbarCategoryView(request):
    category_obj = categoryy.objects.values('id','category')
    category_obj = list(category_obj)[::-1]
    def categoryItems(x):
        def getSingleImage(y):
            return y.split(',')[0]
        if categoryy.objects.filter(id = x).values_list('category',flat=True)[0] == 'All Products':
            products = Product_data.objects.values('id','title','image')
        else:
            products = Product_data.objects.filter(category = x).values('id','title','image')
        products = pd.DataFrame(products)
        products['image'] = products['image'].apply(getSingleImage)
        products = products.to_dict(orient='records')
        return products
    category_obj = pd.DataFrame(category_obj)
    category_obj['items'] = category_obj['id'].apply(categoryItems)
    res = category_obj.to_dict(orient="records")
    return Response(res)

@api_view(['GET'])
def search_bar(request):
    products = Product_data.objects.values('id','title','category','image')
    def getCategoryName(x):
        return categoryy.objects.filter(id = x).values_list('category',flat=True)[0]
    def getSingleImage(x):
        return x.split(',')[0]
    products = pd.DataFrame(products)
    products['category'] = products['category'].apply(getCategoryName)
    products['image'] = products['image'].apply(getSingleImage)
    res = products.to_dict(orient='records')
    return Response(res)

@api_view(['POST'])
def add_to_cart(request):
    data = request.data
    product_id = data['product_id']
    size = data['size']
    price = data['price']
    token = data['token']
    no_login_token = data['no_login_token']
    # print('###########',no_login_token)
    # print('###########token',token)
    no_user_flag = False
    try:
        user = user_data.objects.get(token = token)
        user_id = user.id
    except:
        no_user_flag = True
        if no_login_token == 'null':
            data = noLoginUser(token='token')
            data.save()
            new_id = str(data.id)
            noLoginUser.objects.filter(id = new_id).update(token = make_password(new_id))
            no_login_token = noLoginUser.objects.filter(id = new_id).values_list('token',flat=True)[0]
        else:
            no_login_token = no_login_token
        no_login_id = noLoginUser.objects.filter(token = no_login_token).values_list('id',flat=True)[0]
    if no_user_flag == True:
        data = user_cart(
                            product_id = product_id,
                            size = size,
                            price_per_unit = price,
                            quantity = '1',
                            no_login_id = no_login_id,
                        )
        data.save()
        res = {
                'status':True,
                'token':token,
                'no_login_token':no_login_token,
                'message':'Product added successfully'
              }
    else:
        data = user_cart(
                            user_id = user_id,
                            product_id = product_id,
                            size = size,
                            price_per_unit = price,
                            quantity = '1',
                        )
        data.save()
        res = {
                'status':True,
                'token':token,
                'no_login_token':no_login_token,
                'message':'Product added successfully'
              }
    return Response(res)
    

@api_view(['POST'])
def UserCartView(request):
    data = request.data
    token = data['token']
    no_login_token = data['no_login_token']
    # print('##################',no_login_token)
    no_user_flag = False
    res = {}
    try:
        user = user_data.objects.get(token = token)
        user_id = user.id
    except:
        no_user_flag = True
        try:
            no_user_id = noLoginUser.objects.filter(token = no_login_token).values_list('id',flat=True)[0]
        except:
            no_user_id = 'null'
    if no_user_flag == True:
        cartItems = user_cart.objects.filter(no_login_id = no_user_id).values('id','product_id','size','price_per_unit','quantity')
    else:
        cartItems = user_cart.objects.filter(user_id = user_id).values('id','product_id','size','price_per_unit','quantity')
    def getProductName(x):
        return Product_data.objects.filter(id=x).values_list('title',flat=True)[0]
    def getProductImage(x):
        return Product_data.objects.filter(id = x).values_list('image',flat=True)[0].split(',')[0]
    def getProductPrice(row):
        prod_obj = Product_data.objects.filter(id = row['product_id']).values('size','price').last()
        size = prod_obj['size'].split('|')        
        price = prod_obj['price'].split('|')        
        for i in range(len(size)):
            if size[i] == row['size']:
                return eval(price[i])
    def getDiscountPrice(row):
        prod_obj = Product_data.objects.filter(id = row['product_id']).values('discount','price').last()
        discount = prod_obj['discount']
        return eval(str(row['unit_price'])) - ((eval(str(row['unit_price'])) * 100) // (100 + eval(discount)))
    def calculateNetPrice(row):
        return eval(str(row['unit_price'])) - eval(str(row['discount_price']))
    def calculateTaxPrice(row):
        prod_obj = Product_data.objects.filter(id = row['product_id']).values().last()
        tax = prod_obj['tax']
        return eval(str(row['unit_price'])) - ((eval(str(row['unit_price'])) * 100) // (100 + eval(tax)))
    def calculatePrice(row):
        return eval(str(row['net_price'])) - eval(str(row['tax_price']))
    def calculateFinalPrice(row):
        return eval(str(row['price'])) * eval(str(row['quantity']))
    def calculateFinalTax(row):
        return eval(str(row['tax_price'])) * eval(str(row['quantity']))
    def calculateFinalNetPrice(row):
        return eval(str(row['net_price'])) * eval(str(row['quantity']))
    if len(cartItems) > 0:
        cartItems = pd.DataFrame(cartItems)

        cartItems['id'] = cartItems['id']
        cartItems['name'] = cartItems['product_id'].apply(getProductName)

        cartItems['unit_price'] = cartItems.apply(getProductPrice,axis=1)
        cartItems['discount_price'] = cartItems.apply(getDiscountPrice,axis=1)
        cartItems['net_price'] = cartItems.apply(calculateNetPrice,axis=1)
        cartItems['tax_price'] = cartItems.apply(calculateTaxPrice,axis=1)
        cartItems['price'] = cartItems.apply(calculatePrice,axis=1)

        cartItems['final_net_price'] = cartItems.apply(calculateFinalNetPrice,axis=1)
        cartItems['final_price'] = cartItems.apply(calculateFinalPrice,axis=1)
        cartItems['final_tax'] = cartItems.apply(calculateFinalTax,axis=1)

        cartItems['quantity'] = cartItems['quantity']
        cartItems['size'] = cartItems['size']
        cartItems['image'] = cartItems['product_id'].apply(getProductImage)
        cartItems = cartItems[['product_id','name','unit_price','discount_price','net_price','tax_price','price','final_net_price','final_price','final_tax','quantity','image','size']].to_dict(orient='records')
        res['cartItems'] = cartItems[::-1]

        cart_total = {}
        cartItems = pd.DataFrame(cartItems)
        cart_total['subtotal'] = sum(list(cartItems['final_price']))
        cart_total['shipping'] = 0
        cart_total['tax'] = sum(list(cartItems['final_tax']))
        cart_total['final_price'] = cart_total['subtotal'] + cart_total['shipping'] + cart_total['tax']
        res['cart_total'] = cart_total
    else:
        res['cartItems'] = cartItems
    return Response(res)

@api_view(['POST'])
def CartUpdate(request):
    data = request.data
    product_id = data['prod_id']
    size = data['size']
    update_type = data['update_type']
    token = data['token']
    no_login_token = data['no_login_token']
    try:
        user = user_data.objects.get(token = token)
        user_id = user.id
        cartItems = user_cart.objects.filter(user_id = user_id)
    except:
        no_user = noLoginUser.objects.get(token = no_login_token)
        no_login_id = no_user.id
        cartItems = user_cart.objects.filter(no_login_id = no_login_id)
    
    cart_row = cartItems.filter(product_id=product_id,size=size)
    quantity = int(cart_row.values_list('quantity',flat=True)[0])
    
    if update_type == '+':
        cart_row.update(quantity = str(quantity + 1))
        res = {
                'status':True,
                'message':'Quantity increased successfully'
              }
    elif update_type == '-':
        if quantity > 1:
            cart_row.update(quantity = str(quantity - 1))
            res = {
                    'status':True,
                    'message':'Quantity decreased successfully'
                  }
        else:
            cart_row.delete()
            res = {
                    'status':True,
                    'message':'Item removed from cart'
                  }
    else:
        res = {
                    'status':False,
                    'message':'Something went wrong'
                  }
    return Response(res)

@api_view(['POST'])
def CartitemDelete(request):
    data = request.data
    product_id = data['prod_id']
    size = data['size']
    token = data['token']
    no_login_token = data['no_login_token']
    try:
        user = user_data.objects.get(token = token)
        user_id = user.id
        cartItems = user_cart.objects.filter(user_id = user_id)
    except:
        no_user = noLoginUser.objects.get(token = no_login_token)
        no_login_id = no_user.id
        cartItems = user_cart.objects.filter(no_login_id = no_login_id)
    
    cart_row = cartItems.filter(product_id=product_id,size=size)
    cart_row.delete()
    res = {
            'status':True,
            'message':'Item removed from cart'
          }
    return Response(res)

@api_view(['POST'])
def login(request):
    data = request.data
    no_login_token = data['no_login_token']
    email = data['email']
    password = data['password']
    try:
        user = user_data.objects.get(email = email)
    except:
        res = {
                'status':False,
                'message':'Invalid credentials'
              }
        return Response(res)
    if check_password(password,user.password):
        res = {
                'status':True,
                'message':'login successfull',
                'token':user.token
              }
    else:
        res = {
                'status':False,
                'message':'Invalid Credentials',
                }
        return Response(res)
    if no_login_token != 'null':
        no_user = noLoginUser.objects.get(token = no_login_token)
        no_login_id = no_user.id
        print(no_login_id,"login view")
        no_login_cart = user_cart.objects.filter(no_login_id = no_login_id).values()
        for i in no_login_cart:
            user_cart_row = user_cart.objects.filter(user_id = user.id,product_id = i['product_id'],size = i['size']).values()
            if len(user_cart_row) > 0 :
                quantity = int(i['quantity']) + int(user_cart_row.last()['quantity'])
                user_cart_row.update(quantity = quantity)
                user_cart.objects.filter(id = i['id']).delete()
            else:
                no_login_cart.filter(product_id = i['product_id'],size = i['size']).update(user_id = user.id)
        noLoginUser.objects.filter(id = no_login_id).delete()
    return Response(res)

@api_view(['POST'])
def signUp(request,format=None):
    if request.method == 'POST':
        gender = request.data['gender']
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        email = request.data['email']
        dob = request.data['dob']
        phone_code = request.data['phone_code']
        phone_no = request.data['phone_no']
        password = request.data['password']

        enc_pass = make_password(password)
        token = make_password(email+password)

        if email in user_data.objects.values_list('email',flat=True):
            return Response({'message':'Email already exist',
                            'status':False    
                            })
        if phone_no in user_data.objects.values_list('phone_no',flat=True):
            return Response({'message':'Phone number already exist',
                            'status':False 
                            })
        data = user_data(
                            first_name = first_name,
                            last_name = last_name,
                            email = email,
                            gender = gender,
                            dob = dob,
                            phone_code = phone_code,
                            phone_no = phone_no,
                            password = enc_pass,
                            token = token,
                        )
        data.save()
        new_id = data.id
        add_data = user_address(user_id = new_id)
        add_data.save()
        
        res = { 
                'message':'User created successfully',
                'status':True    
        }   

        return Response(res)

@api_view(['POST'])
def checkout(request):
    data = request.data
    token = data['token']
    res = {}
    try:
        user = user_data.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
              }
        return Response(res)
    res['token'] = token
    personal_info = {}
    personal_info['first_name'] = user.first_name
    personal_info['last_name'] = user.last_name
    personal_info['email'] = user.email
    personal_info['phone_code'] = user.phone_code
    personal_info['phone_number'] = user.phone_no
    res['personal_info'] = personal_info
    address_info = {}
    user_add_obj = user_address.objects.filter(user_id = user.id).values()
    if len(user_add_obj) > 0:
        user_add_obj = user_add_obj.last()
        address_info['address_line_1'] = user_add_obj['add_line_1']
        address_info['address_line_2'] = user_add_obj['add_line_2']
        address_info['city'] = user_add_obj['city']
        address_info['state'] = user_add_obj['state']
        address_info['pincode'] = user_add_obj['country']
        address_info['country'] = user_add_obj['pincode']
    else:
        address_info['address_line_1'] = ""
        address_info['address_line_2'] = ""
        address_info['city'] = ""
        address_info['state'] = ""
        address_info['pincode'] = ""
        address_info['country'] = ""
    res['address_info'] = address_info
    cartItems = user_cart.objects.filter(user_id = user.id).values()
    def getProductName(x):
        return Product_data.objects.filter(id=x).values_list('title',flat=True)[0]
    def getProductImage(x):
        return Product_data.objects.filter(id = x).values_list('image',flat=True)[0].split(',')[0]
    def getProductPrice(row):
        prod_obj = Product_data.objects.filter(id = row['product_id']).values('size','price').last()
        size = prod_obj['size'].split('|')        
        price = prod_obj['price'].split('|')        
        for i in range(len(size)):
            if size[i] == row['size']:
                return eval(price[i])
    def getDiscountPrice(row):
        prod_obj = Product_data.objects.filter(id = row['product_id']).values('discount','price').last()
        discount = prod_obj['discount']
        return eval(str(row['unit_price'])) - ((eval(str(row['unit_price'])) * 100) // (100 + eval(discount)))
    def calculateNetPrice(row):
        return eval(str(row['unit_price'])) - eval(str(row['discount_price']))
    def calculateTaxPrice(row):
        prod_obj = Product_data.objects.filter(id = row['product_id']).values().last()
        tax = prod_obj['tax']
        return eval(str(row['unit_price'])) - ((eval(str(row['unit_price'])) * 100) // (100 + eval(tax)))
    def calculatePrice(row):
        return eval(str(row['net_price'])) - eval(str(row['tax_price']))
    def calculateFinalPrice(row):
        return eval(str(row['price'])) * eval(str(row['quantity']))
    def calculateFinalTax(row):
        return eval(str(row['tax_price'])) * eval(str(row['quantity']))
    def calculateFinalNetPrice(row):
        return eval(str(row['net_price'])) * eval(str(row['quantity']))
    if len(cartItems) > 0:
        cartItems = pd.DataFrame(cartItems)

        cartItems['id'] = cartItems['id']
        cartItems['name'] = cartItems['product_id'].apply(getProductName)

        cartItems['unit_price'] = cartItems.apply(getProductPrice,axis=1)
        cartItems['discount_price'] = cartItems.apply(getDiscountPrice,axis=1)
        cartItems['net_price'] = cartItems.apply(calculateNetPrice,axis=1)
        cartItems['tax_price'] = cartItems.apply(calculateTaxPrice,axis=1)
        cartItems['price'] = cartItems.apply(calculatePrice,axis=1)

        cartItems['final_net_price'] = cartItems.apply(calculateFinalNetPrice,axis=1)
        cartItems['final_price'] = cartItems.apply(calculateFinalPrice,axis=1)
        cartItems['final_tax'] = cartItems.apply(calculateFinalTax,axis=1)

        cartItems['quantity'] = cartItems['quantity']
        cartItems['size'] = cartItems['size']
        cartItems['image'] = cartItems['product_id'].apply(getProductImage)
        cartItems = cartItems[['product_id','name','unit_price','discount_price','net_price','tax_price','price','final_net_price','final_price','final_tax','quantity','image','size']].to_dict(orient='records')
        res['items'] = cartItems
    else:
        res['items'] = []
    cartItems = pd.DataFrame(cartItems)
    res['item_total'] = sum(list(cartItems['final_price'])) 
    res['delivery_charges'] = 0
    res['tax'] = sum(list(cartItems['final_tax']))
    res['order_total'] = res['item_total'] + res['delivery_charges'] + res['tax']
    return Response(res)

@api_view(['POST'])
def userAccountView(request):
    data = request.data
    try:
        token = data['token']
        user = user_data.objects.get(token = token)
        user_add = user_address.objects.get(user_id = str(user.id))
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
              }
        return Response(res)
    res = {}
    res['token'] = token
    res["first_name"] = user.first_name
    res["last_name"] = user.last_name
    res["email"] = user.email
    res["gender"] = user.gender
    res["phone_code"] = user.phone_code
    res["phone_no"] = user.phone_no
    res["dob"] = user.dob

    res["add_line_1"] = user_add.add_line_1
    res["add_line_2"] = user_add.add_line_2
    res["landmark"] = user_add.landmark
    res["city"] = user_add.city
    res["state"] = user_add.state
    res["country"] = user_add.country
    res["pincode"] = user_add.pincode
    return Response(res)

@api_view(['POST'])
def UserAccountEdit(request):
    data = request.data
    try:
        user = user_data.objects.get(token = data['token'])
        user_add = user_address.objects.get(user_id = user.id)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
              }
        return Response(res)
    user_obj = user_data.objects.filter(token = data['token'])
    user_add_obj = user_address.objects.filter(user_id = user.id)
    if len(user_data.objects.exclude(id = user.id).filter(email = data['email']).values_list('email',flat=True))>0:
        res = {
                'status':False,
                'message':'Email already exist'
              }
        return Response(res)
    if len(user_data.objects.exclude(id = user.id).filter(phone_no = data['phone_no']).values_list('phone_no',flat=True))>0:
        res = {
                'status':False,
                'message':'Email already exist'
              }
        return Response(res)
    user_obj.update(
                        first_name = data['first_name'],
                        last_name = data['last_name'],
                        email = data['email'],
                        gender = data['gender'],
                        dob = data['dob'],
                        phone_code = data['phone_code'],
                        phone_no = data['phone_no'],
                    )
    user_add_obj.update(
                        add_line_1 = data['add_line_1'],
                        add_line_2 = data['add_line_2'],
                        landmark = data['landmark'],
                        city = data['city'],
                        state = data['state'],
                        country = data['country'],
                        pincode = data['pincode'],
                       )
    res = {
            'status':True,
            'message':'Profile edited successfully'
          }
    return Response(res)


@api_view(['POST'])
def start_payment(request):
    data = request.data
    try:
        token = data['token']
        user = user_data.objects.get(token = token)
        user_id = user.id
        order_data = {}
        order_data['address_info'] = data['address_info']
        order_data['items'] = data['items']
        order_data['item_total'] = data['item_total']
        order_data['delivery_charges'] = data['delivery_charges']
        order_data['tax'] = data['tax']
        order_data['order_total'] = data['order_total']
    except:
        res = {
                'status':False,
                'message':'Something went wrong',
              }
        return Response(res)
    amount = order_data['order_total']
    order_product = str(order_data['items'])
    client = razorpay.Client(auth=('rzp_test_gHJS0k5aSWUMQc', '8hPVwKRnj4DZ7SB1wyW1miaf'))
    payment = client.order.create({"amount": eval(str(amount)) * 100, 
                                   "currency": "INR", 
                                   "payment_capture": "1"})
    order = PaymentOrder(
                            order_product=order_data, 
                            order_amount=amount, 
                            order_payment_id=payment['id'],
                            user_id=user_id
                        )
    order.save()
    order_id = order.id
    order_data = PaymentOrder.objects.filter(id = order_id).values().last()
    data = {
        "payment": payment,
        "order": order_data
    }
    return Response(data)


@api_view(['POST'])
def handle_payment_success(request):
    res = eval(request.data["response"])
    ord_id =""
    raz_pay_id = ""
    raz_signature = ""
    for key in res.keys():
        if key == 'razorpay_order_id':
            ord_id = res[key]
        elif key == 'razorpay_payment_id':
            raz_pay_id = res[key]
        elif key == 'razorpay_signature':
            raz_signature = res[key]
    order = PaymentOrder.objects.get(order_payment_id=ord_id)
    data = {
            'razorpay_order_id': ord_id,
            'razorpay_payment_id': raz_pay_id,
            'razorpay_signature': raz_signature
            }
    client = razorpay.Client(auth=('rzp_test_gHJS0k5aSWUMQc', '8hPVwKRnj4DZ7SB1wyW1miaf'))
    check = client.utility.verify_payment_signature(data)
    if not check:
        print("Redirect to error url or error page")
        order = PaymentOrder.objects.filter(order_payment_id=ord_id).delete()
        return Response({'error': 'Something went wrong'})
    order.isPaid = True
    order.order_status = 'placed'
    order.save()
    user_cart.objects.filter(user_id = order.user_id).delete()
    res_data = {
                'message': 'payment successfully received!',
                'status':res
                }
    return Response(res_data)

@api_view(['POST'])
def order_view(request):
    data = request.data
    token = data['token']
    try:
        user = user_data.objects.get(token = token)
        user_id = user.id
    except:
        res = {
                'status':False,
                'message':'Something went wrong',
              }
        return Response(res)
    orders = PaymentOrder.objects.filter(user_id = user_id, isPaid = True).values()
    if len(orders)>0:
        def getItemsList(x):
            return eval(x)['items']
        def cropDate(x):
            return dt.strptime(str(x)[:10], '%Y-%m-%d').strftime('%d-%m-%Y')
        orders = pd.DataFrame(orders)
        orders['id'] = orders['id']
        orders['status'] = orders['order_status']
        orders['items'] = orders['order_product'].apply(getItemsList)
        orders['date'] = orders['order_date'].apply(cropDate)
        orders['total_price'] = orders['order_amount']
        orders = orders[['id','status','items','date','total_price']].to_dict(orient='records')
    else:
        orders = []
    res = {
            'status':True,
            'orders':orders,
          }
    return Response(res)

@api_view(['POST'])
def single_order_view(request):
    data = request.data
    token = data['token']
    order_id = data['order_id']
    try:
        user = user_data.objects.get(token = token)
        order = PaymentOrder.objects.get(user_id = user.id,id = order_id)
    except:
        res = {
                'status':False,
                'message':'Something went wrong',
              }
        return Response(res)
    address_info = eval(order.order_product)['address_info']
    res = {}
    res['status'] = order.order_status
    res['items'] = eval(order.order_product)['items']
    res['customer_name'] = user.first_name+' '+user.last_name
    res['phone_code'] = user.phone_code
    res['phone_number'] = user.phone_code
    res['address_line_1'] = address_info['address_line_1']
    res['address_line_2'] = address_info['address_line_2']
    res['city'] = address_info['city']
    res['state'] = address_info['state']
    res['pincode'] = address_info['pincode']
    res['country'] = address_info['country']
    res['item_total'] = eval(order.order_product)['item_total']
    res['delivery_charges'] = eval(order.order_product)['delivery_charges']
    res['order_total'] = eval(order.order_product)['order_total']
    return Response(res)  