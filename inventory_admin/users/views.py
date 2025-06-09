
import json, requests, time, re
import datetime

from decouple import config # type: ignore
from django.http import JsonResponse, response
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.tokens import default_token_generator
# from rest_framework_simplejwt.tokens import RefreshToken

from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FileUploadParser, MultiPartParser
from inventory_admin import constants as const
from users import models

import gspread
# import mysql.connector
from oauth2client.service_account import ServiceAccountCredentials

# 1. Setup Google Sheets connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name('salesSheet.json', scope)
gc = gspread.authorize(credentials)





@api_view(['POST'])
def login_view(request):
    response = {}
    data = json.loads(request.body)
    if data.get('email', None) and data.get('password', None):
        if user:= models.User.objects.filter(email=data.get('email')).first():
            # print(data.get('password'), user.password)
            # valid = check_password(data.get('password'), user.password)
            # if not valid:
            if data.get('password') != user.password:
                response['statusCode'] = const.INVALID_INPUT_ERROR_CODE
                response['message'] = 'Login Failed! Please enter a correct email and password!'
            else:
                if not user.is_active:
                    response['statusCode'] = const.NOT_AUTHORIZED_ERROR_CODE
                    response['message'] = 'Your account is not activated yet!'
                    return JsonResponse(response)
                # if not user.email_verified:
                #     response['statusCode'] = const.EMAIL_NOT_VERIFIED_ERROR_CODE
                #     response['message'] = 'Your email is not verified yet!'
                #     return JsonResponse(response)
                if  data.get('role') != user.role:
                    response['statusCode'] = const.INVALID_INPUT_ERROR_CODE
                    response['message'] = 'Your role is incorrect!'
                    return JsonResponse(response)
                user.last_login = timezone.now()
                user.save()
                # send_welcome_email(user)   # calling temporary, when user first time login               
                
                # response['data'] = get_login_response(user)
                
                response['statusCode'] = const.SUCCESS_STATUS_CODE
                response['message'] = 'Logged in successfully!'
        else:
            response['statusCode'] = const.USER_NOT_REGISTERED_CODE
            response['message'] = "You're not registered. Sign up for free!"
    else:
        response['statusCode'] = const.PARAMETER_MISSING_CODE
        response['message'] = const.PARAMETER_MISSING_OR_INVALID_MESSAGE         
    
    return JsonResponse(response)



@api_view(['POST'])
def signup_view(request):
    response = {}
    data = json.loads(request.body)

    try:
        user = models.User.objects.create(**data)
        response['message'] = 'User created successfully'
        response['user_id'] = str(user.id)
        return JsonResponse(response, status=201)
    except Exception as e:
        response['error'] = str(e)
        return JsonResponse(response, status=400)
    
    
#--------------------------------------------------------------------------




# 2. Open your Google Sheet

@api_view(['POST'])
def fetch_sf_view(request):
    response = {}

    try:
        spreadsheet = gc.open('Report Datasets')
        sheet = spreadsheet.worksheet("Projected Obsolescence (SF)")

        records = sheet.get_all_records()
        saved_items = []

        for row in records:
            # Check if item already exists
            existing_item = models.InventoryItem.objects.filter(
                warehouse=row.get('Warehouse'),
                location=row.get('Location'),
                item_number=row.get('Item #'),
                lot_number=row.get('Lot #'),
                expiration_date=row.get('Expiration Date')
            ).first()

            if existing_item:
                # If exists, add existing item data to response, skip creating
                saved_items.append({
                    "id": existing_item.id,
                    "warehouse": existing_item.warehouse,
                    "location": existing_item.location,
                    "item_name": existing_item.item_name,
                    "lot_number": existing_item.lot_number,
                    "expiration_date": existing_item.expiration_date,
                    "uom": existing_item.uom,
                    "quantity": existing_item.quantity,
                    "price": str(existing_item.price),
                    "value": str(existing_item.value)
                })
            else:
                # Create new item
                item = models.InventoryItem.objects.create(
                    warehouse=row.get('Warehouse'),
                    location=row.get('Location'),
                    item_number=row.get('Item #'),
                    item_name=row.get('Item Name'),
                    lot_number=row.get('Lot #'),
                    expiration_date=row.get('Expiration Date'),
                    quantity=row.get('Qty'),
                    uom=row.get('UOM'),
                    price=row.get('PRICE'),
                    value=row.get('VALUE'),
                )
                saved_items.append({
                    "id": item.id,
                    "warehouse": item.warehouse,
                    "location": item.location,
                    "item_name": item.item_name,
                    "lot_number": item.lot_number,
                    "expiration_date": item.expiration_date,
                    "uom": item.uom,
                    "quantity": item.quantity,
                    "price": str(item.price),
                    "value": str(item.value)
                })

        response['message'] = 'Inventory items saved and fetched successfully!'
        response['data'] = saved_items
        return JsonResponse(response, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@api_view(['POST'])
def fetch_nc_view(request):
    response = {}

    try:
        spreadsheet = gc.open('Report Datasets')
        sheet = spreadsheet.worksheet("Projected Obsolescence (NC)")

        records = sheet.get_all_records()
        saved_items = []

        for row in records:
            # Check if item already exists
            existing_item = models.InventoryItem.objects.filter(
                warehouse=row.get('Warehouse'),
                location=row.get('Location'),
                item_number=row.get('Item #'),
                lot_number=row.get('Lot #'),
                expiration_date=row.get('Expiration Date')
            ).first()

            if existing_item:
                # If exists, add existing item data to response, skip creating
                saved_items.append({
                    "id": existing_item.id,
                    "warehouse": existing_item.warehouse,
                    "location": existing_item.location,
                    "item_name": existing_item.item_name,
                    "lot_number": existing_item.lot_number,
                    "expiration_date": existing_item.expiration_date,
                    "uom": existing_item.uom,
                    "quantity": existing_item.quantity,
                    "price": str(existing_item.price),
                    "value": str(existing_item.value)
                })
            else:
                # Create new item
                item = models.InventoryItem.objects.create(
                    warehouse=row.get('Warehouse'),
                    location=row.get('Location'),
                    item_number=row.get('Item #'),
                    item_name=row.get('Item Name'),
                    lot_number=row.get('Lot #'),
                    expiration_date=row.get('Expiration Date'),
                    quantity=row.get('Qty'),
                    uom=row.get('UOM'),
                    price=row.get('PRICE'),
                    value=row.get('VALUE'),
                )
                saved_items.append({
                    "id": item.id,
                    "warehouse": item.warehouse,
                    "location": item.location,
                    "item_name": item.item_name,
                    "lot_number": item.lot_number,
                    "expiration_date": item.expiration_date,
                    "uom": item.uom,
                    "quantity": item.quantity,
                    "price": str(item.price),
                    "value": str(item.value)
                })

        response['message'] = 'Inventory items saved and fetched successfully!'
        response['data'] = saved_items
        return JsonResponse(response, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
import jwt
import datetime
EmbedSecret = "I7owoLniyj78kABxyaGe4BMNYoVMpE06"
    
@api_view(['GET'])
def embed_token_view(request):
    payload = {
        'embed_user_email': 'viraj@cresitatech.com',  # your Bold BI user email
        'embed_user_name': 'viraj@cresitatech.com',   # any name
        'iss': 'embed',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, EmbedSecret, algorithm='HS256')
    return JsonResponse({'token': token})

    
    
    