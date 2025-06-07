
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