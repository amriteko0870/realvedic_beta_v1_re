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
        admin_login.objects.get(token = token)
    except:
        res = {
                'status':False,
                'message':'Something went wrong'
              }
        return Response(res)
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
        admin_login.objects.get(token = token)
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
            admin_login.objects.get(token = token)
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
        res = {
                "status":True,
                "message":"product added successfuly" 
              }
        return Response(res)


