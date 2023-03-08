from import_statements import *

# Create your views here.

@api_view(['POST'])
def login(request):
    data = request.data
    email = data['email']
    password = data['password']
    try :
        user = admin_login.objects.get(email = email)
    except:
        res ={
                'status':False,
                'message':'Invalid credentials'
             }
        return Response(res)
    
    if check_password(password,user.password):
        res ={
                'status':True,
                'message':'Login successfull',
                'token': user.token,
             }
    else:
        res ={
                'status':False,
                'message':'Invalid credentials'
             }
    return Response(res)

@api_view(['POST'])
def adminProductView(request):
    data = request.data
    token = data['token']
    try:
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
              }
        return Response(res)
    res = {}
    def getCategoryName(x):
        return categoryy.objects.filter(id = x).values_list('category',flat=True)[0]
    titles = ['Product ID','Name','Category','HSN','Stock','Status','Action']
    res['titles'] = titles
    content = Product_data.objects.values('id','title','category','HSN','status')
    content = pd.DataFrame(content)
    content['product_id'] = content['id']
    content['product_name'] = content['title']
    content['category'] = content['category'].apply(getCategoryName)
    content['hsn'] = content['HSN']
    content['stock'] = 'N/A'
    content['status'] = content['status']
    content = content[['product_id','product_name','category','hsn','stock','status']].to_dict(orient='records')
    res['content'] = content[::-1]
    status = [
                {
                "name": "In stock",
                "color": "#00ac69",
                },
                {
                "name": "Out of stock",
                "color": "#FF0000",
                },
             ]
    res['status'] = status
    return Response(res)

@api_view(['POST'])
def adminProductDelete(request):
    data = request.data
    product_id = data['product_id']
    token = data['token']
    try:
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
              }
        return Response(res)
    log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = Product_data.objects.filter(id = product_id).values().last()['title'] + ' was deleted'
                        )
    log_obj.save()
    Product_data.objects.filter(id = product_id).delete()
    res = {
            'status':True,
            'message':'Product deleted successfully',
          }
    return Response(res)

@api_view(['POST'])
def singleProductView(request):
    data = request.data
    token = data['token']
    product_id = data['product_id']
    try:
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
              }
        return Response(res)
    res = {}
    product_obj = Product_data.objects.filter(id = product_id).values().last()
    images = product_obj['image'].split(',')
    images = [i for i in images if i != '']
    images = images if len(images) == 5 else images + (5-len(images)) * [False] 
    res['token'] = token
    res['images'] = images
    res['name'] = product_obj['title']
    res['id'] = product_obj['id']
    res['status'] = "Active" if product_obj['status'] else "Inactive"
    res['category'] = categoryy.objects.filter(id = product_obj['category']).annotate(name = F('category')).values('id','name').last()
    res['hsn'] = product_obj['HSN']
    res['discount'] = product_obj['discount']
    res['tax'] = product_obj['tax']
    if product_obj['size'].split('|')[0] != '':
        variant_data = pd.DataFrame({
                                        'variant_name':product_obj['size'].split('|'),
                                        'price':product_obj['price'].split('|'),
                                        'sku':product_obj['SKU'].split('|')
                                    })
        variant_data['id'] = variant_data.index
        variant_data = variant_data.to_dict(orient='records')
    else:
        variant_data = []
    res['variant_data'] = variant_data
    sibling_product = Product_data.objects.filter(id = product_obj['sibling_product'])\
                                          .annotate(product_id = F('id'),product_name = F('title'),img = F('image'))\
                                          .values('product_id','product_name','img','category').last()
    sibling_product['img'] = sibling_product['img'].split(',')[0] if len(sibling_product['img'].split(',')) > 0 else []
    sibling_product['category'] = categoryy.objects.filter(id = sibling_product['category']).values_list('category',flat=True)[0]
    res['sibling_product'] = sibling_product
    nutritional_info = pd.DataFrame({
                                    "value":product_obj['nutrition'].split('|') if len(product_obj['nutrition'].split('|')) == 4 else ['0 g','0 g','0 g','0 Kcal'],
                                    "n_name":['Total Fat','Protien','Carbohydrate','Energy']})
    nutritional_info['n_value'] = nutritional_info['value'].apply(lambda x: x.split(" ")[0])
    nutritional_info['n_unit'] = nutritional_info['value'].apply(lambda x: x.split(" ")[1])
    nutritional_info['id'] = nutritional_info.index
    nutritional_info = nutritional_info[['id','n_name','n_value','n_unit']].to_dict(orient='records')
    res['nutritional_info'] = nutritional_info
    meta_fields = pd.DataFrame({
                                'm_name':['About','Benefits','Ingredients','How to use','How we make it'],
                                'm_value':[product_obj['about'],product_obj['benefits'],product_obj['ingredients'],product_obj['how_to_use'],product_obj['how_we_make_it']]
                               })
    meta_fields['id'] = meta_fields.index
    meta_fields = meta_fields.to_dict(orient='records')
    res['meta_fields'] = meta_fields
    res['status_list'] = ["Active", "Inactive"]
    category_list = categoryy.objects.exclude(category = "All Products").annotate(name = F('category')).values('id','name')
    res['category_list'] = category_list
    return Response(res)

@api_view(['POST'])
def siblingProductList(request):
    data = request.data
    try:
        product_id = data['product_id']
    except:
        product_id = -1
    token = data['token']
    try:
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
              }
        return Response(res)
    def getCategoryName(x):
        return categoryy.objects.filter(id = x).values_list('category',flat=True)[0]
    prod_list = Product_data.objects.exclude(id = product_id)\
                                    .annotate(product_id = F('id'),product_name = F('title'),img = F('image'))\
                                    .values('product_id','product_name','img','category')
    prod_list = pd.DataFrame(prod_list)
    prod_list['category'] = prod_list['category'].apply(getCategoryName)    
    prod_list['img'] = prod_list['img'].apply(lambda x : x.split(',')[0])
    prod_list = prod_list.to_dict(orient='records')
    return Response(prod_list)


@api_view(['POST'])
def storeImage(request):
    img = request.FILES['file']
    array = request.data['array']
    array = array.replace("true", "True")
    array = array.replace("false", "False")
    array = eval(array)
    index = int(request.data['index'])
    img_path = 'img/'
    fs = FileSystemStorage()
    img_path = img_path+img.name
    uploaded_file = fs.save(img_path, img)
    updated_value = 'media/'+uploaded_file
    array[index] = updated_value
    res = {'status':True,
           'array':array}
    return Response(res)

@api_view(['POST'])
def singleProductEdit(request):
    data = request.data
    token = data['token']
    try:
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
              }
        return Response(res)
    image = [i for i in data['images'] if i != False]
    image = ','.join(image)
    title = data['name']
    product_id = data['id']
    status = True if data['status'] == "Active" else False
    category = data['category']['id']
    HSN = data['hsn']
    discount = data['discount']
    tax = data['tax']
    variants = pd.DataFrame(data['variant_data'])
    size = '|'.join(list(variants['variant_name']))
    price = '|'.join(list(variants['price']))
    SKU = '|'.join(list(variants['sku']))
    sibling_product = data['sibling_product']['product_id']
    nutritional_info = pd.DataFrame(data['nutritional_info'])
    nutritional_info['full_value'] = nutritional_info['n_value'] + ' ' + nutritional_info['n_unit']
    nutrition = '|'.join(list(nutritional_info['full_value']))
    about = data['meta_fields'][0]['m_value']
    benefits = data['meta_fields'][1]['m_value']
    ingredients = data['meta_fields'][2]['m_value']
    how_to_use = data['meta_fields'][3]['m_value']
    how_we_make_it = data['meta_fields'][4]['m_value']
    Product_data.objects.filter(id = product_id).update(
                                                            title = title,
                                                            category = category,
                                                            about = about,
                                                            image = image,
                                                            price = price,
                                                            size = size,
                                                            discount = discount,
                                                            tax = tax,
                                                            benefits = benefits,
                                                            ingredients = ingredients,
                                                            how_to_use = how_to_use,
                                                            how_we_make_it = how_we_make_it,
                                                            nutrition = nutrition,
                                                            status = status,
                                                            sibling_product = sibling_product,
                                                            HSN = HSN,
                                                            SKU = SKU,
                                                        )
    log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = Product_data.objects.filter(id = product_id).values().last()['title'] + ' was edited'
                        )
    log_obj.save()
    res = {
            "status":True,
            "message":"product updated successfuly" 
            }
    
    return Response(res)

@api_view(['POST','PUT'])
def addNewProduct(request):
    if request.method == 'POST':
        data = request.data
        token = data['token']
        try:
            admin_login.objects.get(token = token)
        except:
            res = {
                    'status':False,
                    'message':'Something went wrong'
                }
            return Response(res)
        res = {}
        res['token'] = token
        res['images'] = 5 * [False]
        res['name'] = ''
        res['status'] = "Active"
        res['category'] = ""
        res['hsn'] = ""
        res['discount'] = ""
        res['tax'] = ""
        res['variant_data'] = []
        res['sibling_product'] = {}
        nutritional_info = pd.DataFrame({
                                        "value":['0 g','0 g','0 g','0 Kcal'],
                                        "n_name":['Total Fat','Protien','Carbohydrate','Energy']})
        nutritional_info['n_value'] = nutritional_info['value'].apply(lambda x: x.split(" ")[0])
        nutritional_info['n_unit'] = nutritional_info['value'].apply(lambda x: x.split(" ")[1])
        nutritional_info['id'] = nutritional_info.index
        nutritional_info = nutritional_info[['id','n_name','n_value','n_unit']].to_dict(orient='records')
        res['nutritional_info'] = nutritional_info
        meta_fields = pd.DataFrame({
                                    'm_name':['About','Benefits','Ingredients','How to use','How we make it'],
                                    'm_value':['','','','','']
                                })
        meta_fields['id'] = meta_fields.index
        meta_fields = meta_fields.to_dict(orient='records')
        res['meta_fields'] = meta_fields
        res['status_list'] = ["Active", "Inactive"]
        category_list = categoryy.objects.exclude(category = "All Products").annotate(name = F('category')).values('id','name')
        res['category_list'] = category_list
        return Response(res)
    
    if request.method == 'PUT':
        data = request.data['data']
        token = data['token']
        try:
            a_user = admin_login.objects.get(token = token)
        except:
            res = {
                    'status':False,
                    'message':'Something went wrong'
                }
            return Response(res)
        image = [i for i in data['images'] if i != False]
        image = ','.join(image)
        title = data['name']
        status = True if data['status'] == "Active" else False
        category = data['category']['id']
        HSN = data['hsn']
        discount = data['discount']
        tax = data['tax']
        variants = pd.DataFrame(data['variant_data'])
        size = '|'.join(list(variants['variant_name']))
        price = '|'.join(list(variants['price']))
        SKU = '|'.join(list(variants['sku']))
        sibling_product = data['sibling_product']['product_id']
        nutritional_info = pd.DataFrame(data['nutritional_info'])
        nutritional_info['full_value'] = nutritional_info['n_value'] + ' ' + nutritional_info['n_unit']
        nutrition = '|'.join(list(nutritional_info['full_value']))
        about = data['meta_fields'][0]['m_value']
        benefits = data['meta_fields'][1]['m_value']
        ingredients = data['meta_fields'][2]['m_value']
        how_to_use = data['meta_fields'][3]['m_value']
        how_we_make_it = data['meta_fields'][4]['m_value']
        data = Product_data(
                                title = title,
                                category = category,
                                about = about,
                                image = image,
                                price = price,
                                size = size,
                                discount = discount,
                                tax = tax,
                                benefits = benefits,
                                ingredients = ingredients,
                                how_to_use = how_to_use,
                                how_we_make_it = how_we_make_it,
                                nutrition = nutrition,
                                status = status,
                                sibling_product = sibling_product,
                                HSN = HSN,
                                SKU = SKU,
                            )
        data.save()
        log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = Product_data.objects.filter(id = data.id).values().last()['title'] + ' was created'
                        )
        log_obj.save()
        res = {
                "status":True,
                "message":"product added successfuly" 
              }
        return Response(res)


@api_view(['POST'])
def adminOrderView(request):
    data = request.data
    try:
        token = data['token']
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    res = {}
    def getCustomerDetails(x):
        u = user_data.objects.filter(id = x).values().last()
        return { "name": u['first_name']+ " "+ u["last_name"],"email":u['email']}
    titles = ["Order ID","Timestamp","Customer","Items","State","Grand Total","Delivery Status","Actions"]
    res['titles'] = titles
    content = PaymentOrder.objects.values()
    content = pd.DataFrame(content)
    content['invoice_id'] = content['id']
    content['created_date'] = content['order_date'].apply(lambda x : str(x)[:10])
    content['created_time'] = content['order_date'].apply(lambda x : str(x)[11:19])
    content['customer'] = content['user_id'].apply(getCustomerDetails)
    content['items'] = content['order_product'].apply(lambda x : len(eval(x)['items']))
    content['destination_state'] = content['order_product'].apply(lambda x : eval(x)['address_info']['state'])
    content['grand_total'] = content['order_amount']
    content['status'] = content['order_status']
    content['is_paid'] = content['isPaid']
    content['admin_placed'] = content['admin_placed_status']
    content = content[['invoice_id','created_date','created_time','customer','items','destination_state','grand_total','status','is_paid','admin_placed']].to_dict(orient='records')
    res['content'] = content
    return Response(res)

@api_view(['POST'])
def singleOrderView(request):
    data = request.data
    try:
        token = data['token']
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    order_id = data['order_id']
    order_obj = PaymentOrder.objects.filter(id = order_id).values().last()
    res = {}
    def getCategoryName(x):
        cat_id = Product_data.objects.filter(id = x).values_list('category',flat=True)[0]
        return categoryy.objects.filter(id = cat_id).values_list('category',flat=True)[0]
    res['order_id'] = order_obj['id']
    res['status'] = order_obj['order_status']
    res['order_date'] = order_obj['order_date'][:10]
    res['order_time'] = order_obj['order_date'][11:19]
    items = eval(order_obj['order_product'])['items']
    items = pd.DataFrame(items)
    items['id'] = items['product_id']
    items['image'] = items['image']
    items['title'] = items['name']
    items['unit_price'] = items['unit_price']
    items['net_price'] = items['net_price']
    items['size'] = items['size']
    items['quantity'] = items['quantity']
    items['quantity_price'] = items['price']
    items['category'] = items['category']
    items = items[['id','image','title','unit_price','net_price','size','quantity','quantity_price','category']].to_dict(orient='records')
    res['items'] = items
    payment_info = {}
    payment_info["sub_total"] = eval(order_obj['order_product'])['item_total']
    payment_info["shipping"] = eval(order_obj['order_product'])['delivery_charges']
    payment_info["grand_total"] = eval(order_obj['order_product'])['order_total']
    res['payment_info'] = payment_info
    shipping_info = {}
    shipping_info["address_line_1"] = eval(order_obj['order_product'])['address_info']['address_line_1']
    shipping_info["address_line_2"] = eval(order_obj['order_product'])['address_info']['address_line_2']
    shipping_info["landmark"] = eval(order_obj['order_product'])['address_info']['landmark']
    shipping_info["city"] = eval(order_obj['order_product'])['address_info']['city']
    shipping_info["state"] = eval(order_obj['order_product'])['address_info']['state']
    shipping_info["country"] = eval(order_obj['order_product'])['address_info']['country']
    res['shipping_info'] = shipping_info
    res['billing_info'] = shipping_info
    contact_info = {}
    user_obj = user_data.objects.filter(id = order_obj['user_id']).values().last()
    contact_info["first_name"] = user_obj['first_name']
    contact_info["last_name"] = user_obj['last_name']
    contact_info["email"] = user_obj['email']
    contact_info["phone_number"] = "+"+user_obj['phone_code']+" "+user_obj['phone_no']
    res['contact_info'] = contact_info
    status_list =  [
                        { "status_name": 'placed', "status_color": '#f3a638' },
                        { "status_name": 'processed', "status_color": '#54b7d3' },
                        { "status_name": 'dispatched', "status_color": '#1e91cf' },
                        { "status_name": 'on the way', "status_color": '#7955bf' },
                        { "status_name": 'delivered', "status_color": '#00ac69' },
                        { "status_name": 'canceled', "status_color": '#FF0000' },
                        { "status_name": 'returned', "status_color": '#e99f15' },
                   ]
    res['status_list'] = status_list
    return Response(res)

@api_view(['POST'])
def singleOrderEdit(request):
    data = request.data
    try:
        token = data['token']
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    order_id = data['order_id']
    order_status = data['order_status']
    try:
        PaymentOrder.objects.get(id = order_id)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    order_obj = PaymentOrder.objects.filter(id = order_id).update(order_status = order_status)
    log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'Order status with this order id '+order_id + ' was changed to '+order_status
                        )
    log_obj.save()
    res = {
                'status':True,
                'message':'Order updated successfully'
            }
    return Response(res)

@api_view(['POST'])
def getProductList(request):
    data = request.data
    try:    
        token = data['token']
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    res = {}
    def getAfterDicountPriceArray(x):
        dis = x['discount']
        net_price = []
        if x['price'].split('|')[0] != '':
            for i in x['price'].split('|'):
                net_price.append(round(int(i) - (int(i)*int(dis)/100)))
        return net_price
    res['added_products'] = []
    all_products = Product_data.objects.values()
    all_products = pd.DataFrame(all_products)
    all_products['id'] = all_products['id']
    all_products['title'] = all_products['title']
    all_products['category'] = all_products['category'].apply( lambda x : categoryy.objects.filter(id = x).values_list('category',flat=True)[0])
    all_products['image'] = all_products['image'].apply(lambda x : x.split(',')[0])
    all_products['size'] = all_products['size'].apply(lambda x : x.split('|'))
    all_products['unit_price'] = all_products['price'].apply(lambda x : x.split('|'))
    all_products['net_price'] = all_products.apply(getAfterDicountPriceArray,axis=1)
    all_products = all_products[['id','title','category','image','size','unit_price','net_price']]
    all_products = all_products.to_dict(orient='records')
    res['all_products'] = all_products
    payment_details =  {
                            'sub_total': '',
                            'shipping': '',
                            'tax': '',
                            'total': '',
                        }
    res['payment_details'] = payment_details
    user_list = user_data.objects.values('first_name','last_name','email','id')
    res['user_list'] = user_list
    shipping_info = {}
    shipping_info["address_line_1"] = ''
    shipping_info["address_line_2"] = ''
    shipping_info["landmark"] = ''
    shipping_info["city"] = ''
    shipping_info["state"] = ''
    shipping_info["country"] = ''
    res['shipping_info'] = shipping_info
    customer_details = {}
    customer_details["id"] = ''
    customer_details["first_name"] = ''
    customer_details["last_name"] = ''
    customer_details["email"] = ''
    customer_details["phone_number"] = ''
    res['customer_details'] = customer_details
    return Response(res)

@api_view(['POST'])
def orderUserDetails(request):
    data = request.data
    try:    
        token = data['token']
        admin_login.objects.get(token = token)
        user_data.objects.get(id = data['user_id'])
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    user_obj = user_data.objects.filter(id = data['user_id']).values().last()
    res = {}
    customer_details = {}
    customer_details["id"] = user_obj['id']
    customer_details["first_name"] = user_obj['first_name']
    customer_details["last_name"] = user_obj['last_name']
    customer_details["email"] = user_obj['email']
    customer_details["phone_number"] = "+"+user_obj['phone_code']+" "+user_obj['phone_no']
    res['customer_details'] = customer_details
    user_add = user_address.objects.filter(user_id = data['user_id']).values().last()
    shipping_info = {}
    shipping_info["address_line_1"] = user_add['add_line_1']
    shipping_info["address_line_2"] = user_add['add_line_2']
    shipping_info["landmark"] = user_add['landmark']
    shipping_info["city"] = user_add['city']
    shipping_info["state"] = user_add['state']
    shipping_info["country"] = user_add['country']
    shipping_info['pincode'] = user_add['pincode']
    res['shipping_info'] = shipping_info
    return Response(res)
@api_view(['POST'])
def updateAddedProducts(request):
    data = request.data
    try:    
        token = data['token']
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    res = {}
    flag = False
    added_products = eval(data['added_products'])
    for i in added_products:
        if data['prod_id'] == str(i['product_id']) and data['size'] == i['size']:
            i['quantity'] = int(i['quantity']) + 1
            i['price'] = i['net_price'] * int(i['quantity'])
            flag = True
    if not flag:
        prod_obj = Product_data.objects.filter(id = data['prod_id']).values().last()
        single_prod_obj = {}
        single_prod_obj['product_id'] = prod_obj['id']
        single_prod_obj['name'] = prod_obj['title']
        single_prod_obj['category'] = categoryy.objects.filter(id = prod_obj['category']).values_list('category',flat=True)[0]
        single_prod_obj['image'] = prod_obj['image'].split(',')[0]
        single_prod_obj['size'] = [i for i in prod_obj['size'].split('|') if i == data['size']][0]
        single_prod_obj['unit_price'] = [int(prod_obj['price'].split('|')[i]) for i in range(len(prod_obj['size'].split('|'))) if prod_obj['size'].split('|')[i] == data['size']][0]
        single_prod_obj['net_price'] = round(single_prod_obj['unit_price'] - (single_prod_obj['unit_price'] * int(prod_obj['discount'])/100))
        single_prod_obj['quantity'] = '1'
        single_prod_obj['price'] = single_prod_obj['net_price'] * int(single_prod_obj['quantity'])
        added_products.append(single_prod_obj)
    res['added_products'] = added_products
    if len(added_products) > 0:
        payment = pd.DataFrame(added_products)
        sub_total = sum(list(payment['price']))
        shipping = shipping_price.objects.values().last()['price'] if sub_total < 500 else 0
        total = sub_total + shipping
        payment_details =  {
                                'sub_total': sub_total,
                                'shipping': shipping,
                                'total': total,
                            }
    else:
        payment_details =  {
                                'sub_total': '',
                                'shipping': '',
                                'total': '',
                            }
    res['payment_details'] = payment_details
    return Response(res)

@api_view(['POST'])
def updateAddedProductsQuantity(request):
    data = request.data
    try:    
        token = data['token']
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    res = {}
    added_products = eval(data['data'])
    if data['update_type'] == '+':
        added_products[int(data['index'])]['quantity'] = int(added_products[int(data['index'])]['quantity']) + 1
        added_products[int(data['index'])]['price'] = added_products[int(data['index'])]['net_price'] * int(added_products[int(data['index'])]['quantity'])
    else:
        if int(added_products[int(data['index'])]['quantity']) > 1:
            added_products[int(data['index'])]['quantity'] = int(added_products[int(data['index'])]['quantity']) - 1
            added_products[int(data['index'])]['price'] = added_products[int(data['index'])]['net_price'] * int(added_products[int(data['index'])]['quantity'])

        else:
            del added_products[int(data['index'])]
    res['added_products'] = added_products
    if len(added_products) > 0:
        payment = pd.DataFrame(added_products)
        sub_total = sum(list(payment['price']))
        shipping = shipping_price.objects.values().last()['price'] if sub_total < 500 else 0
        total = sub_total + shipping
        payment_details =  {
                                'sub_total': sub_total,
                                'shipping': shipping,
                                'total': total,
                            }
    else:
        payment_details =  {
                                'sub_total': '',
                                'shipping': '',
                                'total': '',
                            }
    res['payment_details'] = payment_details
    return Response(res)

@api_view(['POST'])
def updateAddedProductsDelete(request):
    data = request.data
    try:    
        token = data['token']
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    res = {}
    added_products = eval(data['data'])
    del added_products[int(data['index'])]
    res['added_products'] = added_products
    if len(added_products) > 0:
        payment = pd.DataFrame(added_products)
        sub_total = sum(list(payment['price']))
        shipping = shipping_price.objects.values().last()['price'] if sub_total < 500 else 0
        total = sub_total + shipping
        payment_details =  {
                                'sub_total': sub_total,
                                'shipping': shipping,
                                'total': total,
                            }
    else:
        payment_details =  {
                                'sub_total': '',
                                'shipping': '',
                                'total': '',
                            }
    res['payment_details'] = payment_details
    return Response(res)

@api_view(['POST'])
def userView(request):
    data = request.data
    try:    
        token = data['token']
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    res = {}
    def createUserObj(x):
        return {"name":x['first_name'] + " " + x["last_name"],'email':x['email']}
    titles =  ["User ID","Created","Customer","Phone No","Actions"]
    res['titles'] = titles
    content = user_data.objects.values()
    content = pd.DataFrame(content)
    content['user_id'] = content['id']
    content['created_date'] = content['created_at'].apply(lambda x : str(x)[:10])
    content['created_time'] = content['created_at'].apply(lambda x : str(x)[11:19])
    content['user'] = content.apply(createUserObj,axis = 1)
    content['phone_no'] = content.apply(lambda x : "+"+x['phone_code']+" "+x["phone_no"],axis=1)
    content['status'] = content['status']
    content = content[['user_id','created_date','created_time','user','phone_no','status']].to_dict(orient='records')
    res['content'] = content
    return Response(res)

@api_view(['POST'])
def singleUserView(request):
    data = request.data
    try:    
        token = data['token']
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    res = {}
    def setOrderItems(x):
        x = eval(x)['items']
        items = pd.DataFrame(x)
        items["image"] = items['image']
        items["title"] = items['name']
        items["quantity"] = items['quantity']
        items["weight"] = items['size']
        items["price"] = items['price']
        items = items[['image','title','quantity','weight','price']].to_dict(orient='records')
        return items
    user_id = data['user_id']
    user_obj = user_data.objects.filter(id = user_id).values().last()
    user_add_obj = user_address.objects.filter(user_id = user_id).values().last()
    order_obj = PaymentOrder.objects.filter(user_id = user_id)
    res["first_name"] = user_obj['first_name']
    res["last_name"] = user_obj['last_name']
    res["email"] = user_obj['email']
    res["phone_number"] = "+" + user_obj['phone_code'] + " " + user_obj['phone_no']
    if len(order_obj.values()) > 0:
        res["total_amount_spent"] = sum([int(i) for i in order_obj.values_list('order_amount',flat=True)])
        res["total_orders"] = order_obj.count() 
        orders = pd.DataFrame(order_obj.values())
        orders['order_id'] = orders['id']
        orders['status'] = orders['order_status']
        orders['order_total'] = orders['order_amount']
        orders['order_time'] = orders['order_date'].apply(lambda x : str(x)[11:19])
        orders['order_date'] = orders['order_date'].apply(lambda x : str(x)[:10])
        orders['items'] = orders['order_product'].apply(setOrderItems)
        orders =  orders[['order_id','status','order_total','order_time','order_date','items']].to_dict(orient='records')
        res['orders'] = orders
    else:
        res["total_amount_spent"] = "0"
        res["total_orders"] = "0"
        res['orders'] = []
    shipping_info = {}
    if len(user_add_obj) > 0:
        shipping_info["address_line_1"] = user_add_obj['add_line_1'] 
        shipping_info["address_line_2"] = user_add_obj['add_line_2']
        shipping_info["landmark"] = user_add_obj['landmark']
        shipping_info["city"] = user_add_obj['city']
        shipping_info["state"] = user_add_obj['state']
        shipping_info["country"] = user_add_obj['country']
        shipping_info["pincode"] = user_add_obj['pincode']
    res['shipping_info'] = shipping_info
    return Response(res)

@api_view(['PATCH'])
def userBlock(request):
    data = request.data
    try:    
        token = data['token']
        a_user = admin_login.objects.get(token = token)
        user = user_data.objects.get(id = data['user_id'])
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    if user.status:
        status = False
        message = "User blocked successfully"
        log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'user with id '+ str(user.id) +' and name '+ str(user.first_name)+' '+str(user.last_name)+' was blocked'
                        )
        log_obj.save()
    else:
        status = True
        message = "User unblocked successfully"
        log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'user with id '+ str(user.id) +' and name '+ str(user.first_name)+' '+str(user.last_name)+' was unblocked'
                        )
        log_obj.save()
    user_data.objects.filter(id = data['user_id']).update(status = status)
    
    res = {
            'status' : True,
            'message': message 
          }
    return Response(res)

@api_view(['POST'])
def addUser(request):
    data = request.data
    print(data)
    try:    
        token = data['token']
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    if data["email"] in user_data.objects.values_list('email',flat=True):
            return Response({'message':'Email already exist',
                            'status':False    
                            })
    if data["phone_no"] in user_data.objects.values_list('phone_no',flat=True):
        return Response({'message':'Phone number already exist',
                        'status':False 
                        })
    user_data_obj = user_data(
                        first_name = data['first_name'],
                        last_name = data['last_name'],
                        email = data['email'],
                        gender = data['gender'],
                        dob = data['dob'],
                        phone_code = data['isd'],
                        phone_no = data['phone_no'],
                        admin_create_status = True,
    )
    user_data_obj.save()
    new_id = user_data_obj.id
    user_add_data = user_address(
                                    user_id = new_id,
                                    add_line_1 = data['address_line_1'],  
                                    add_line_2 = data['address_line_2'],
                                    landmark = data['landmark'],              
                                    city = data['city'],
                                    state = data['state'],
                                    country = data['country'],
                                    pincode = data['zip'],
                                )
    
    user_add_data.save()
    log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'user with id '+ str(user_data_obj.id) +' and name '+ str(user_data_obj.first_name)+' '+str(user_data_obj.last_name)+' was created'
                        )
    log_obj.save()
    res = {
            'status':True,
            'message':'User added successfully'
          }
    return Response(res)

@api_view(['POST'])
def adminStartPayment(request):
    data = request.data
    try:    
        token = data['token']
        admin_login.objects.get(token = token)
        user = user_data.objects.get(id = data['customer_details']['id'])
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    order_data = {}
    order_data['address_info'] = data['shipping_info']
    order_data['items'] = data['added_products']
    order_data['item_total'] = data['payment_details']['sub_total']
    order_data['delivery_charges'] = data['payment_details']['shipping']
    order_data['order_total'] = data['payment_details']['total']
    amount = order_data['order_total']
    client = razorpay.Client(auth=(os.getenv('key_id'),os.getenv('key_secret') ))
    payment = client.order.create({"amount": eval(str(amount)) * 100, 
                                   "currency": "INR", 
                                   "payment_capture": "1"})
    order = PaymentOrder(
                            order_product=order_data, 
                            order_amount=amount, 
                            order_payment_id=payment['id'],
                            user_id=str(data['customer_details']['id']),
                            admin_placed_status = True,
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
def adminHandlePaymentSuccess(request):
    data = request.data
    try:    
        token = data['token']
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
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
    client = razorpay.Client(auth=(os.getenv('key_id'),os.getenv('key_secret') ))
    check = client.utility.verify_payment_signature(data)
    if not check:
        order = PaymentOrder.objects.filter(order_payment_id=ord_id).delete()
        return Response({'message': 'Something went wrong','status':False})
    order.isPaid = True
    order.order_status = 'placed'
    order.save()
    log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'Order with order id '+ str(order.id)+' was created by payment method'
                        )
    log_obj.save()
    res_data = {
                'message': 'payment successfully received!',
                'status':True
                }
    return Response(res_data)


@api_view(['POST'])
def adminOrderMarkAsPaid(request):
    data = request.data
    try:    
        token = data['token']
        a_user = admin_login.objects.get(token = token)
        user = user_data.objects.get(id = data['customer_details']['id'])
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    order_data = {}
    order_data['address_info'] = data['shipping_info']
    order_data['items'] = data['added_products']
    order_data['item_total'] = data['payment_details']['sub_total']
    order_data['delivery_charges'] = data['payment_details']['shipping']
    order_data['order_total'] = data['payment_details']['total']
    amount = order_data['order_total']
    order = PaymentOrder(
                            order_product=order_data, 
                            order_amount=amount, 
                            order_payment_id="null",
                            user_id=str(data['customer_details']['id']),
                            order_status = 'placed',
                            admin_placed_status = True,
                        )
    order.save()
    log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'Order with order id '+ str(order.id)+' was created by Mark as paid method'
                        )
    log_obj.save()
    res = {
                'message': 'Order received successfully!',
                'status':True
          }
    return Response(res)

@api_view(['POST'])
def bannerUploadCategoryProducts(request):
    data = request.data
    try:    
        token = data['token']
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    res = {}
    category_list = categoryy.objects.exclude(category = 'All Products').annotate(name = F('category')).values('id','name')
    res['category_list'] = category_list
    product_list = Product_data.objects.annotate(name = F('title')).values('id','name')
    res['product_list'] = product_list
    return Response(res)

@api_view(['POST'])
def bannerImageUpload(request):
    data = request.data
    try:    
        token = data['token']
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    img = request.FILES['file']
    img_path = 'img/'
    pil_img = PIL.Image.open(img)
    wid, hgt = pil_img.size
    if wid < 1000 or hgt < 400:
        res = {'status':False,'message':'Please provide minimum required resolution'}
        return Response(res)
    else:
        if 2.6 > wid/hgt >= 2.5:
            pass
        else:
            res = {'status':False,'message':'Image does not meet required aspect ratio'}
            return Response(res)
        
    fs = FileSystemStorage()
    img_path = img_path+img.name
    uploaded_file = fs.save(img_path, img)
    updated_value = 'media/'+uploaded_file
    
    res = {'status':True,
           'image':updated_value}
    return Response(res)


@api_view(['POST'])
def heroBannerImageUpload(request):
    data = request.data
    try:    
        token = data['token']
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    img = request.FILES['file']
    banner_type = data['banner_type']
    img_path = 'img/'
    pil_img = PIL.Image.open(img)
    wid, hgt = pil_img.size
    if banner_type == 'mobile':
        r_wid = 600
        r_hgt = 300
        r_aspect_ratio = 2.0
    elif banner_type == 'desktop':
        r_wid = 900
        r_hgt = 200
        r_aspect_ratio = 4.5
    if wid < r_wid or hgt < r_hgt:
        res = {'status':False,'message':'Please provide minimum required resolution'}
        return Response(res)
    else:
        if r_aspect_ratio + 0.1 > wid/hgt >= r_aspect_ratio:
            pass
        else:
            res = {'status':False,'message':'Image does not meet required aspect ratio'}
            return Response(res)
        
    fs = FileSystemStorage()
    img_path = img_path+img.name
    uploaded_file = fs.save(img_path, img)
    updated_value = 'media/'+uploaded_file
    
    res = {'status':True,
           'image':updated_value}
    return Response(res)



@api_view(['POST'])
def largeCarousalImagesUpload(request):
    data = request.data
    try:    
        token = data['token']
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    if data['banner_type'] == 'offer':
        banner_obj = images_and_banners(
                                            title = 'large_carousal_images',
                                            image = data['desktop_image'],
                                            product_id = str(data['selected_id']),
                                            type = 'p' if data['offer_type'] == 'products' else 'c',
                                        )
        if data['offer_type'] == 'products':
            Product_data.objects.filter(id = data['selected_id']).update(discount = data['discount'])
        else:
            Product_data.objects.filter(category = data['selected_id']).update(discount = data['discount'])
    else:
        banner_obj = images_and_banners(
                                            title = 'large_carousal_images',
                                            image = data['desktop_image'],
                                       )
    
    banner_obj.save()
    log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'Offer section banner was added'
                        )
    log_obj.save()
    res = {
            'status':True,
            'message':'Banner added successfully'
    }
    return Response(res)


@api_view(['POST'])
def bannerImagesUpload(request):
    data = request.data
    try:    
        token = data['token']
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    banner_obj = images_and_banners(
                                    title = 'banner',
                                    image = data['hero_desktop'],
                                    mobile_image = data['hero_mobile'] 
                                    )
    banner_obj.save()
    log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'Hero section banner was added'
                        )
    log_obj.save()
    res = {
            'status':True,
            'message':'Banner added successfully'
    }
    return Response(res)


@api_view(['POST'])
def adminBannerView(request):
    data = request.data
    try:    
        token = data['token']
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    res = {}
    title = ['Image', 'Banner Type', 'Usage In', 'Offer', 'Action']
    hero = {}
    hero['title'] = title
    content = images_and_banners.objects.filter(title = 'banner').values()
    content = pd.DataFrame(content)
    content['img_id'] = content['id']
    content['image'] = content['image']
    content['banner_type'] = content['type'].apply(lambda x : 'Offer' if x != '' else 'Normal')
    content['use_in'] = content['type'].apply(lambda x : 'Product' if x == 'p' else 'category' if x == 'c' else '-')
    content['discount'] = content['discount'].apply(lambda x : str(x)+' %' if x != '' else '-')
    content = content[['img_id','image','banner_type','use_in','discount']]
    content = content.to_dict(orient='records')
    hero['content'] = content
    res['hero'] = hero

    offer = {}
    offer['title'] = title
    content = images_and_banners.objects.filter(title = 'large_carousal_images').values()
    content = pd.DataFrame(content)
    content['img_id'] = content['id']
    content['image'] = content['image']
    content['banner_type'] = content['type'].apply(lambda x : 'Offer' if x != '' else 'Normal')
    content['use_in'] = content['type'].apply(lambda x : 'Product' if x == 'p' else 'category' if x == 'c' else '-')
    content['discount'] = content['discount'].apply(lambda x : str(x)+' %' if x != '' else '-')
    content = content[['img_id','image','banner_type','use_in','discount']]
    content = content.to_dict(orient='records')
    offer['content'] = content
    res['offer'] = offer
    return Response(res)

@api_view(['POST'])
def deleteBanner(request):
    data = request.data
    try:    
        token = data['token']
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    banner_type = data['banner_type']
    images_and_banners.objects.filter(id = data['img_id']).delete()
    if banner_type == 'h':
        log_obj = actionLogs(
                                user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                                log_message  = 'Hero section banner was deleted'
                            )
        log_obj.save()
    elif banner_type == 'o':
        log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'Offer section banner was deleted'
                        )
        log_obj.save()
    res = {
            'status':True,
            'message':'Delete Successful'
          }
    return Response(res)

@api_view(['POST'])
def adminCategoryListView(request):
    data = request.data
    try:    
        token = data['token']
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    title = ['ID', 'Name', 'Baner', 'Icon', 'Action']
    res = {}
    res['title'] = title
    content = categoryy.objects.exclude(category = 'All Products').values()
    content = pd.DataFrame(content)
    content['id'] = content['id']
    content['name'] = content['category']
    content['desktop_banner'] = content['category_banner'] 
    content['mobile_banner'] = content['category_banner_mobile'] 
    content['icon'] = content['category_image']
    content['status'] = content['status']
    content = content[['id','name','desktop_banner','mobile_banner','icon','status']]
    content = content.to_dict(orient= 'records')
    res['content'] = content
    return Response(res)

@api_view(['POST','PUT'])
def adminEditCategory(request):
    if request.method == 'POST':
        data = request.data
        try:    
            token = data['token']
            admin_login.objects.get(token = token)
        except:
            res = {
                    'status':False,
                    'message':'Something went wrong'
                }
            return Response(res)
        cat_obj = categoryy.objects.filter(id = data['cat_id']).values().last()
        res = {}
        res['token'] = token
        res['cat_id'] = cat_obj['id']
        res['name'] = cat_obj['category']
        res['desktop_banner'] = cat_obj['category_banner'] 
        res['mobile_banner'] = cat_obj['category_banner_mobile'] 
        res['icon'] = cat_obj['category_image'] 
        return Response(res)
    if request.method == 'PUT':
        data = request.data
        try:    
            token = data['token']
            a_user = admin_login.objects.get(token = token)
        except:
            res = {
                    'status':False,
                    'message':'Something went wrong'
                }
            return Response(res)
        categoryy.objects.filter(id = data['cat_id']).update(
                                                                category = data['name'],
                                                                category_banner = data['desktop_banner'],
                                                                category_banner_mobile = data['mobile_banner'],
                                                                category_image = data['icon'],
                                                            )
        log_obj = actionLogs(
                                user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                                log_message  = 'category with name '+ categoryy.objects.filter(id = data['cat_id']).values().last()['category']+' was edited'
                            )
        log_obj.save()
        res = {
                'status':True,
                'message':'Category updated successfully'
              }
        return Response(res)


@api_view(['POST'])
def categoryIconUpload(request):
    img = request.FILES['file']
    if str(img.name).split('.')[1] == 'svg':
        fs = FileSystemStorage()
        img_path = 'img/'
        img_path = img_path+img.name
        uploaded_file = fs.save(img_path, img)
        updated_value = 'media/'+uploaded_file
        res = {'status':True,
           'image':updated_value}
    else:
        res = {'status':False,
           'message':'Only SVG file allowed'}
    return Response(res)


@api_view(['POST'])
def adminCreateCategory(request):
    data = request.data
    try:    
        token = data['token']
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    try:
        category = data['name']
        category_banner = data['desktop_banner']
        category_banner_mobile = data['mobile_banner']
        category_image = data['icon']
    except:
        res = {
                'status':False,
                'message':'All field are required'
            }
        return Response(res)
    cat_obj = categoryy(
                            category = data['name'],
                            category_banner = data['desktop_banner'],
                            category_banner_mobile = data['mobile_banner'],
                            category_image = data['icon'],
                        )
    cat_obj.save()
    log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'category with name '+ cat_obj.category+' was created'
                        )
    log_obj.save()
    res = {'status':True,'message':'Category created successfully'}
    return Response(res) 
    
@api_view(['POST'])
def adminCategoryDeactivate(request):
    data = request.data
    try:    
        token = data['token']
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    d_type = data['d_type']
    cat_id = data['cat_id']
    if d_type == 'c':
        categoryy.objects.filter(id = cat_id).update(status = False)
        log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'category with name '+ categoryy.objects.filter(id = data['cat_id']).values().last()['category']+' was deactivated without products'
                            )
        log_obj.save()
        res = {
                'status':True,
                'message':'Category deactivated successfully'
              }
    elif d_type == 'b':
        prod_list = Product_data.objects.filter(category = cat_id,status = True).values_list('id',flat=True)
        prod_list = map(str, prod_list)
        categoryy.objects.filter(id = cat_id).update(status = False,deactivated_products = ','.join(list(prod_list)))
        Product_data.objects.filter(category = cat_id).update(status = False)
        log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'category with name '+ categoryy.objects.filter(id = data['cat_id']).values().last()['category']+' was deactivated with products'
                            )
        log_obj.save()
        res = {
                'status':True,
                'message':'Category and products deactivated successfully'
              }
    return Response(res)
        
@api_view(['POST'])
def adminCategoryActivate(request):
    data = request.data
    try:    
        token = data['token']
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    cat_id = data['cat_id']
    cat_obj = categoryy.objects.filter(id = cat_id)
    deactivated_prod = cat_obj.values().last()['deactivated_products'].split(',')
    deactivated_prod = [0] if deactivated_prod[0] == '' else deactivated_prod
    cat_obj.update(status = True)
    Product_data.objects.filter(id__in = deactivated_prod).update(status = True)
    log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'category with name '+ categoryy.objects.filter(id = data['cat_id']).values().last()['category']+' was activated'
                            )
    log_obj.save()
    res = { 
            'status':True,
            'message':'Category activated successfully'
          }
    return Response(res)

@api_view(['POST'])
def adminDeleteCategory(request):
    data = request.data
    try:    
        token = data['token']
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    log_obj = actionLogs(
                            user = a_user.first_name + ' ' + a_user.last_name + '|' + a_user.email,
                            log_message  = 'category with name '+ categoryy.objects.filter(id = data['cat_id']).values().last()['category']+' was deleted'
                        )
    log_obj.save()
    categoryy.objects.filter(id = data['cat_id']).delete()
    Product_data.objects.filter(category = data['cat_id']).delete()
    res = {
            'status':True,
            'message':'Category Deleted successfully'
           }
    return Response(res)

@api_view(['POST'])
def adminLogView(request):
    data = request.data
    try:    
        token = data['token']
        a_user = admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
            }
        return Response(res)
    res = {}
    title = ['Name', 'Log Message', 'Date', 'Time']
    res['title'] = title
    log_obj = actionLogs.objects.values()[::-1]
    log_obj = pd.DataFrame(log_obj)
    log_obj['id'] = log_obj['id']
    log_obj['name'] = log_obj['user']
    log_obj['log'] = log_obj['log_message']
    log_obj['date'] = log_obj['date_time'].apply(lambda x : str(x)[:10])
    log_obj['time'] = log_obj['date_time'].apply(lambda x : str(x)[11:19])
    log_obj = log_obj[['id','name','log','date','time']]
    log_obj = log_obj.to_dict(orient='records')
    res['content'] = log_obj
    return Response(res)