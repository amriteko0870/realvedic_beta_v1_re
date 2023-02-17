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
        print("no_login_token",no_login_token)
        no_login_id = noLoginUser.objects.filter(token = no_login_token).values_list('id',flat=True)
        print("no_login_id",no_login_id)
        if len(no_login_id) > 0:
            cart_product_ids = user_cart.objects.filter(no_login_id = str(no_login_id[0])).values_list('product_id',flat=True)
            print("cart_product_ids",cart_product_ids)
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
        if len(cart_product_ids > 0):
            quantity = cart_product_ids[0]
            cart_status = True
        else:
            quantity = 0
            cart_status = False
    except:
        no_login_token = request.data['no_login_token']
        no_login_id = noLoginUser.objects.filter(token = no_login_token).values_list('id',flat=True)
        cart_product_ids = user_cart.objects.filter(no_login_id = no_login_id[0],product_id=product_id).values_list('quantity',flat=True)
        print('cart_product_ids',cart_product_ids)
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
        print("no_login_token",no_login_token)
        no_login_id = noLoginUser.objects.filter(token = no_login_token).values_list('id',flat=True)
        print("no_login_id",no_login_id)
        if len(no_login_id) > 0:
            cart_product_ids = user_cart.objects.filter(no_login_id = str(no_login_id[0])).values_list('product_id',flat=True)
            print("cart_product_ids",cart_product_ids)
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
    print('##################',no_login_token)
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
    def priceCalculate(up,q):
        return int(up)*int(q)
    def getProductImage(x):
        return Product_data.objects.filter(id = x).values_list('image',flat=True)[0].split(',')[0]
    def getProductPrice(row):
        prod_obj = Product_data.objects.filter(id = row['product_id']).values('size','price').last()
        size = prod_obj['size'].split('|')        
        price = prod_obj['price'].split('|')        
        for i in range(len(size)):
            if size[i] == row['size']:
                return price[i]
    if len(cartItems) > 0:
        cartItems = pd.DataFrame(cartItems)

        cartItems['id'] = cartItems['id']
        cartItems['name'] = cartItems['product_id'].apply(getProductName)
        cartItems['unit_price'] = cartItems.apply(getProductPrice,axis=1)
        cartItems['price'] = cartItems.apply(lambda x: priceCalculate(x.unit_price, x.quantity), axis=1)
        cartItems['quantity'] = cartItems['quantity']
        cartItems['size'] = cartItems['size']
        cartItems['image'] = cartItems['product_id'].apply(getProductImage)
        cartItems = cartItems[['product_id','name','unit_price','price','quantity','image','size']].to_dict(orient='records')
        res['cartItems'] = cartItems

        cart_total = {}
        cartItems = pd.DataFrame(cartItems)
        cart_total['subtotal'] = sum(list(cartItems['price']))
        cart_total['shipping'] = 90
        cart_total['tax'] = 70
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
        cartItems = user_cart.objects.filter(user_id = user_id).values()
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
        no_login_cart = user_cart.objects.filter(no_login_id = no_login_id).values()
        for i in no_login_cart:
            user_cart_row = user_cart.objects.filter(product_id = i['product_id'],size = i['size']).values()
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
        if phone_no in user_data.objects.values_list('email',flat=True):
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
    def priceCalculate(up,q):
        return int(up)*int(q)
    def getProductImage(x):
        return Product_data.objects.filter(id = x).values_list('image',flat=True)[0].split(',')[0]
    def getProductPrice(row):
        prod_obj = Product_data.objects.filter(id = row['product_id']).values('size','price').last()
        size = prod_obj['size'].split('|')        
        price = prod_obj['price'].split('|')        
        for i in range(len(size)):
            if size[i] == row['size']:
                return price[i]
    if len(cartItems) > 0:
        cartItems = pd.DataFrame(cartItems)

        cartItems['id'] = cartItems['id']
        cartItems['title'] = cartItems['product_id'].apply(getProductName)
        cartItems['unit_price'] = cartItems.apply(getProductPrice,axis=1)
        cartItems['price'] = cartItems.apply(lambda x: priceCalculate(x.unit_price, x.quantity), axis=1)
        cartItems['quantity'] = cartItems['quantity']
        cartItems['size'] = cartItems['size']
        cartItems['image'] = cartItems['product_id'].apply(getProductImage)
        cartItems = cartItems[['id','title','price','quantity','image']].to_dict(orient='records')
        res['items'] = cartItems
    else:
        res['items'] = []
    cartItems = pd.DataFrame(cartItems)
    res['item_total'] = sum(list(cartItems['price']))
    res['delivery_charges'] = 90
    res['tax'] = 70
    res['order_total'] = res['item_total'] + res['delivery_charges'] + res['tax']
    return Response(res)