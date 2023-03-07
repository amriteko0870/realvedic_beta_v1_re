from import_statements import *

@api_view(['POST'])
def categoryPage2(request):
    data = request.data
    category_id = data['category']
    category_obj = categoryy.objects.exclude(status = False).filter(id = category_id).values().last()
    res={}
    no_login_status = False#,
    try:
        token = data['token']
        user = user_data.objects.get(token = token)
        cart_product_ids = user_cart.objects.filter(user_id = user.id).values_list('product_id',flat=True)
        cart_status_user_id = str(user.id)#,
    except:
        no_login_status = True#,
        no_login_token = data['no_login_token']
        no_login_id = noLoginUser.objects.filter(token = no_login_token).values_list('id',flat=True)
        if len(no_login_id) == 0:
            no_login_id = ['']
        if len(no_login_id) > 0:
            cart_product_ids = user_cart.objects.filter(no_login_id = str(no_login_id[0])).values_list('product_id',flat=True)
            cart_status_user_id = str(no_login_id[0])#,

        else:           
            cart_status_user_id = 'u'#,
            cart_product_ids = []
    res['category'] = category_obj['category']
    res['category_banner'] = category_obj['category_banner']
    res['category_mobile_banner'] = category_obj['category_banner_mobile']
    if category_obj['category'] == 'All Products':
        products = Product_data.objects.exclude(status = False).values('id','title','image','size','price','discount')
    else:
        products = Product_data.objects.exclude(status = False).filter(category = category_id).values('id','title','image','size','price','discount')
    
    def getSingleImage(x):
        return x.split(',')[0]
    def splitByPipe(x):
        return x.split('|')
    def cartStatusCheck(x):
        if str(x) in cart_product_ids:
            return True
        else:
            return False
    def getCartStatusArray(row):#,
        p_id = row['id']
        sizes = row['size'].split('|')
        user_id = row['user_id'].split('_')
        cart_status_array = []
        if user_id[0] == 'u':
            for size in sizes:
                if len(user_cart.objects.filter(user_id = user_id[1],product_id = p_id,size = size).values()):
                    cart_status_array.append(True)
                else:
                    cart_status_array.append(False)
        else:
            for size in sizes:
                if len(user_cart.objects.filter(no_login_id = user_id[1],product_id = p_id,size = size).values()):
                    cart_status_array.append(True)
                else:
                    cart_status_array.append(False)
        return cart_status_array

    def getDiscountPrice(row):
        prod_obj = Product_data.objects.filter(id = row['id']).values('discount','price').last()
        discount = prod_obj['discount']
        discount_array = []
        for i in prod_obj['price'].split('|'):
            discount_array.append(eval(str(i)) - ((eval(str(i)) * 100) // (100 + eval(discount))))
        # return eval(str(row['unit_price'])) - ((eval(str(row['unit_price'])) * 100) // (100 + eval(discount)))
        return discount_array
    def getNetPriceArray(x):
        net_price = []
        for i in range(len(x['unit_price'])):
            net_price.append(str(round(int(x['unit_price'][i]) - (int(x['discount'][i])))))
        return net_price
    
    products = pd.DataFrame(products)
    if no_login_status:#,
        df_user_id = 'n_'+cart_status_user_id
    else:
        df_user_id = 'u_'+cart_status_user_id
    products['user_id'] = df_user_id#,
    products['image'] = products['image'].apply(getSingleImage)
    products['weight'] = products['size'].apply(splitByPipe)
    products['unit_price'] = products['price'].apply(splitByPipe)
    products['discount'] = products.apply(getDiscountPrice,axis=1)
    products['net_price'] = products.apply(getNetPriceArray,axis=1)
    products['cart_status'] = products['id'].apply(cartStatusCheck)
    products['cart_status_array'] = products.apply(getCartStatusArray,axis=1)#,
    products = products[['id','title','image','weight','unit_price','net_price','cart_status','cart_status_array']].to_dict(orient="records")
    res['products'] = products
    return Response(res)


@api_view(['POST'])
def landing_page2(request):
    data = request.data
    token = data['token']
    no_login_status = False#,
    try:
        user_data.objects.get(token = token)
        user = user_data.objects.get(token = token)
        cart_product_ids = user_cart.objects.filter(user_id = user.id).values_list('product_id',flat=True)
        cart_status_user_id = str(user.id)#,
    except:
        no_login_status = True#,
        no_login_token = data['no_login_token']
        no_login_id = noLoginUser.objects.filter(token = no_login_token).values_list('id',flat=True)
        if len(no_login_id) == 0:
            no_login_id = ['']
        if len(no_login_id) > 0:
            cart_product_ids = user_cart.objects.filter(no_login_id = str(no_login_id[0])).values_list('product_id',flat=True)
            cart_status_user_id = str(no_login_id[0])#,
        else:           
            cart_status_user_id = 'u'#,
            cart_product_ids = []
    
    res = {}
    category_obj = categoryy.objects.exclude(category = 'All Products').exclude(status = False).annotate(
                                                title = F('category'),
                                                image = F('category_image')
                                             )\
                                    .values('id','title','image','status')
    category_obj_all_prod = categoryy.objects.filter(category = 'All Products').annotate(
                                                title = F('category'),
                                                image = F('category_image')
                                             )\
                                    .values('id','title','image','status')
    res['tab'] = list(category_obj_all_prod)+list(category_obj)[::-1]
    res['banner'] = images_and_banners.objects.filter(title = 'banner').values()
    res['mobile_banner'] = images_and_banners.objects.filter(title = 'banner').values()
    def singleImageGet(x):
        return x.split(',')[0]
    def splitPipe(x):
        return x.split('|')
    def cartStatusCheck(x):
        if str(x) in cart_product_ids:
            return True
        else:
            return False
    def getCartStatusArray(row):#,
        p_id = row['id']
        sizes = row['size'].split('|')
        user_id = row['user_id'].split('_')
        cart_status_array = []
        # print(user_id,"cartstatusarray")
        if user_id[0] == 'u':
            for size in sizes:
                if len(user_cart.objects.filter(user_id = user_id[1],product_id = p_id,size = size).values()) > 0:
                    cart_status_array.append(True)
                else:
                    cart_status_array.append(False)
        else:
            for size in sizes:
                if len(user_cart.objects.filter(no_login_id = user_id[1],product_id = p_id,size = size).values()) > 0:
                    cart_status_array.append(True)
                else:
                    cart_status_array.append(False)
        return cart_status_array
    
    def getDiscountPrice(row):
        prod_obj = Product_data.objects.filter(id = row['id']).values('discount','price').last()
        discount = prod_obj['discount']
        discount_array = []
        for i in prod_obj['price'].split('|'):
            discount_array.append(eval(str(i)) - ((eval(str(i)) * 100) // (100 + eval(discount))))
        # return eval(str(row['unit_price'])) - ((eval(str(row['unit_price'])) * 100) // (100 + eval(discount)))
        return discount_array
    def getNetPriceArray(x):
        net_price = []
        for i in range(len(x['unit_price'])):
            net_price.append(str(round(int(x['unit_price'][i]) - (int(x['discount'][i])))))
        return net_price
        # return eval(str(x['unit_price'])) - eval(str(x['discount_price']))

    top_seller = Product_data.objects.exclude(status = False).values('id','image','title','size','price','discount')
    top_seller = pd.DataFrame(top_seller)
    if no_login_status:#,
        df_user_id = 'n_'+cart_status_user_id
    else:
        df_user_id = 'u_'+cart_status_user_id
    top_seller['user_id'] = df_user_id#,
    top_seller['image'] = top_seller['image'].apply(singleImageGet)
    top_seller['weight'] = top_seller['size'].apply(splitPipe)
    top_seller['unit_price'] = top_seller['price'].apply(splitPipe)
    top_seller['discount'] = top_seller.apply(getDiscountPrice,axis=1)
    top_seller['net_price'] = top_seller.apply(getNetPriceArray,axis=1)
    top_seller['cart_status'] = top_seller['id'].apply(cartStatusCheck)
    top_seller['cart_status_array'] = top_seller.apply(getCartStatusArray,axis=1)#,
    top_seller = top_seller[['id','image','title','weight','unit_price','net_price','cart_status','cart_status_array']].to_dict(orient='records')
    top_seller = list(top_seller)[::-1][:5]
    res['top_seller_products'] = top_seller
    # print(top_seller,"landing page")

    small_crousel = Product_data.objects.annotate(
                                                    product_id = F('id')
                                                 )\
                                        .values('product_id','title','image')
    small_crousel = list(small_crousel)[::-1][:10]
    small_crousel = pd.DataFrame(small_crousel)
    small_crousel['image'] = small_crousel['image'].apply(singleImageGet)
    small_crousel = small_crousel.to_dict(orient='records')
    res['small_carousal_images'] = small_crousel

    large_crousel = images_and_banners.objects.filter(title='large_carousal_images')\
                                              .values('image','product_id','type')
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
def single_product_view2(request):
    product_id=request.data["prod_id"]
    product_info = Product_data.objects.filter(id = product_id).values().last()
    res = {}
    no_login_status = False#,
    if not Product_data.objects.filter(id = product_id).values().last()['status']:
        res = {
                'status':False,
                'message':'Product not available'
              }
        return Response(res)
    try:
        token = request.data['token']
        user = user_data.objects.get(token = token)
        # print('userrrrrrrrrrr',user.id)
        cart_product_ids = user_cart.objects.filter(user_id = user.id,product_id=product_id).values_list('quantity',flat=True)
        cart_status_user_id = str(user.id)#,
        if len(cart_product_ids) > 0:
            quantity = cart_product_ids[0]
            cart_status = True
        else:
            quantity = 0
            cart_status = False
    except:
        no_login_status = True#,
        no_login_token = request.data['no_login_token']
        no_login_id = noLoginUser.objects.filter(token = no_login_token).values_list('id',flat=True)
        if len(no_login_id) == 0:
            no_login_id = ['']
        if len(no_login_id) > 0:#,
            cart_status_user_id = str(no_login_id[0])#,
        else:#,
            cart_status_user_id = 'u'#,
        cart_product_ids = user_cart.objects.filter(no_login_id = no_login_id[0],product_id=product_id).values_list('quantity',flat=True)

        if len(cart_product_ids) > 0:
            quantity = cart_product_ids[0]
            cart_status = True
        else:           
            quantity = 0
            cart_status = False
    def getCartStatusArray(p_id,sizes,user_id):#,
        p_id = p_id
        sizes = sizes.split('|')
        user_id = user_id.split('_')
        cart_status_array = []
        if user_id[0] == 'u':
            for size in sizes:
                if len(user_cart.objects.filter(user_id = user_id[1],product_id = p_id,size = size).values()):
                    cart_status_array.append(True)
                else:
                    cart_status_array.append(False)
        else:
            for size in sizes:
                if len(user_cart.objects.filter(no_login_id = user_id[1],product_id = p_id,size = size).values()):
                    cart_status_array.append(True)
                else:
                    cart_status_array.append(False)
        return cart_status_array
    if no_login_status:#,
        df_user_id = 'n_'+cart_status_user_id
    else:
        df_user_id = 'u_'+cart_status_user_id
    
    product_details = {}
    product_details['id'] = product_info['id']
    product_details['title'] = product_info['title']
    product_details['description'] = product_info['about']
    product_details['original_price'] = product_info['price'].split('|')[0]
    product_details['offer_price'] = str(round((int(product_info['price'].split('|')[0]) * 100)/(100 + int(product_info['discount']))))
    product_details['images'] = product_info['image'].split(',')
    product_details['quantity'] = quantity
    product_details['cart_status'] = cart_status
    product_details['cart_status_array'] = getCartStatusArray(product_info['id'],product_info['size'],df_user_id)
    product_details['pack_size'] = pd.DataFrame(
                                                    {
                                                        'weight':product_info['size'].split('|'),
                                                        'price':product_info['price'].split('|'),
                                                        'offer_price': map(lambda x : str(round((int(x) * 100)//(100 + int(product_info['discount'])))),
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
    res['status'] = True
    return Response(res)



@api_view(['POST'])
def recently_viewed_oc(request):
    data = request.data
    res={}
    no_login_status = False#,
    try:
        token = data['token']
        user = user_data.objects.get(token = token)
        cart_product_ids = user_cart.objects.filter(user_id = user.id).values_list('product_id',flat=True)
        cart_status_user_id = str(user.id)#,
    except:
        no_login_status = False#,
        no_login_token = data['no_login_token']
        no_login_id = noLoginUser.objects.filter(token = no_login_token).values_list('id',flat=True)
        if len(no_login_id) == 0:
            no_login_id = ['']
        if len(no_login_id) > 0:
            cart_product_ids = user_cart.objects.filter(no_login_id = str(no_login_id[0])).values_list('product_id',flat=True)
            cart_status_user_id = str(no_login_id[0])#,

        else:           
            cart_status_user_id = 'u'#,
            cart_product_ids = []

    products = Product_data.objects.exclude(status = False).values('id','title','image','size','price','discount')[:5]
    
    def getSingleImage(x):
        return x.split(',')[0]
    def splitByPipe(x):
        return x.split('|')
    def cartStatusCheck(x):
        if str(x) in cart_product_ids:
            return True
        else:
            return False
    def getCartStatusArray(row):#,
        p_id = row['id']
        sizes = row['size'].split('|')
        user_id = row['user_id'].split('_')
        cart_status_array = []
        if user_id[0] == 'u':
            for size in sizes:
                if len(user_cart.objects.filter(user_id = user_id[1],product_id = p_id,size = size).values()):
                    cart_status_array.append(True)
                else:
                    cart_status_array.append(False)
        else:
            for size in sizes:
                if len(user_cart.objects.filter(no_login_id = user_id[1],product_id = p_id,size = size).values()):
                    cart_status_array.append(True)
                else:
                    cart_status_array.append(False)
        return cart_status_array
    def getDiscountPrice(row):
        prod_obj = Product_data.objects.filter(id = row['id']).values('discount','price').last()
        discount = prod_obj['discount']
        discount_array = []
        for i in prod_obj['price'].split('|'):
            discount_array.append(eval(str(i)) - ((eval(str(i)) * 100) // (100 + eval(discount))))
        # return eval(str(row['unit_price'])) - ((eval(str(row['unit_price'])) * 100) // (100 + eval(discount)))
        return discount_array
    def getNetPriceArray(x):
        net_price = []
        for i in range(len(x['unit_price'])):
            net_price.append(str(round(int(x['unit_price'][i]) - (int(x['discount'][i])))))
        return net_price
    
    products = pd.DataFrame(products)
    if no_login_status:#,
        df_user_id = 'n_'+cart_status_user_id
    else:
        df_user_id = 'u_'+cart_status_user_id
    products['user_id'] = df_user_id#,
    products['image'] = products['image'].apply(getSingleImage)
    products['weight'] = products['size'].apply(splitByPipe)
    products['unit_price'] = products['price'].apply(splitByPipe)
    products['discount'] = products.apply(getDiscountPrice,axis=1)
    products['net_price'] = products.apply(getNetPriceArray,axis=1)
    products['cart_status'] = products['id'].apply(cartStatusCheck)
    products['cart_status_array'] = products.apply(getCartStatusArray,axis=1)#,
    products = products[['id','title','image','weight','unit_price','net_price','cart_status','cart_status_array']].to_dict(orient="records")
    return Response(products)