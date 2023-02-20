import numpy as np
import pandas as pd
import time
from datetime import datetime as dt
import datetime
import re
from operator import itemgetter 
import os
import random


#-------------------------Django Modules---------------------------------------------
from django.http import Http404, HttpResponse, JsonResponse,FileResponse
from django.shortcuts import render
from django.db.models import Avg,Count,Case, When, IntegerField,Sum,FloatField,CharField
from django.db.models import F,Func,Q
from django.db.models import Value as V
from django.db.models.functions import Concat,Cast,Substr
from django.contrib.auth.hashers import make_password,check_password
from django.db.models import Min, Max
from django.db.models import Subquery
#----------------------------restAPI--------------------------------------------------
from rest_framework.decorators import parser_classes,api_view
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.response import Response

#------------------------------razorpay---------------------------------------------
import razorpay

#--------------------------- user models -------------------------------------------
from realvedic_app.models import user_data
from realvedic_app.models import user_address
from realvedic_app.models import user_cart
from realvedic_app.models import categoryy
from realvedic_app.models import Product_data
from realvedic_app.models import images_and_banners
from realvedic_app.models import blogs
from realvedic_app.models import categoryy
from realvedic_app.models import noLoginUser
from realvedic_app.models import PaymentOrder

# -------------------------- admin model ---------------------------------------------
from admin_realvedic_app.models import admin_login
