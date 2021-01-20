from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token, logout
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import F
from django.contrib.auth.models import User
from .models import *

DEFAULT_MAIL_FOLDERS = ['inbox', 'sent', 'important', 'draft', 'trash']

def ping(request):
    return JsonResponse({'status': 'Api working'})

@csrf_exempt
def login(request):
    print(request)
    user_info = {}
    user_info['username'] = request.POST.get('username')
    user_info['password'] = request.POST.get('password') 
    print(user_info)
    user = authenticate(username=user_info['username'], password=user_info['password'])
    print(user)
    del user_info["password"]
    if user is None:
        json_response = {
            'status': 'error',
            'message': 'Incorrect username or password.'
        }
        return JsonResponse(json_response)
    else:
        token, created = Token.objects.get_or_create(user=user)
        print(token)
        response = JsonResponse({
            'status': 'success',
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'message': 'Successfully logged in.'
        })
        return response

@csrf_exempt
def create_user(request):
    try:
        user_data = {}
        user_data['username'] = request.POST.get('username', None)
        user_data['email'] = request.POST.get('email', None)
        user_data['password'] = request.POST.get('password')
        user = User.objects.create_user(user_data['username'], user_data['email'], user_data['password'], last_login=timezone.now())
        try:
            user.save()
        except IntegrityError:
            return JsonResponse({
                'status': 'error',
                'message': 'Error creating user.'
            })
        for folder in DEFAULT_MAIL_FOLDERS:
            mail_folder = Mail_Folder()
            mail_folder.folder_name = folder
            mail_folder.user = user
            mail_folder.unread_count = 0
            mail_folder.save()
        return JsonResponse({'status': 'User created successfully'})
    except Exception as e:
        print(e)
        return JsonResponse({"status":"error"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def send_mail(request):
    mail_details = Mail()
    user= request.user
    to_user_email = request.POST.get('to_user_email', None)
    to_user = None
    try:
        print(to_user_email)
        to_user = User.objects.get(email=to_user_email)
    except:
        print('To user not found')
    mail_details.from_user = user
    if to_user:
        mail_details.to_user = to_user
    mail_details.user = user
    mail_details.folder_name = 'inbox'
    mail_details.content = request.POST.get('content', '')
    mail_details.subject = request.POST.get('subject', '')
    mail_details.save()
    if to_user:
        mail_folder = Mail_Folder.objects.get(user = to_user, folder_name='inbox')
        mail_folder.unread_count = mail_folder.unread_count + 1
        mail_folder.save()
    else:
        mail_folder = Mail_Folder.objects.get(user = user, folder_name='draft')
        mail_folder.unread_count = mail_folder.unread_count + 1
        mail_folder.save()
    return JsonResponse({'status': 'success'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_mails(request, folder_name):
    user = request.user
    page = request.GET.get('page', 1)
    size = request.GET.get('size', 50)
    print(folder_name)
    if folder_name == 'inbox':
        mail_list = Mail.objects.filter(to_user=user, folder_name=folder_name)
        print()
    elif folder_name == 'sent':
        mail_list = Mail.objects.filter(from_user=user, folder_name=folder_name)
    mail_list = list(mail_list.annotate(username=F('from_user__username')).values('id', 'folder_name', 'username', 'subject', 'category', 'label', 'created_at', 'is_read'))
    
    if page and size and mail_list:
        paginator = Paginator(mail_list, size)
        mail_list = paginator.page(page).object_list
    return JsonResponse({'status': 'success', 'mail_list': mail_list})

def mark_mail_read(mail_id, folder_name, user):
    mail_details = Mail.objects.get(id=mail_id, to_user=user, folder_name=folder_name)
    if not mail_details.is_read:
        mail_details.is_read = True
        mail_details.save()
        mail_folder = Mail_Folder.objects.get(user = user, folder_name=folder_name)
        mail_folder.unread_count = mail_folder.unread_count - 1
        mail_folder.save()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_mail_details(request, mail_id, folder_name):
    print(mail_id, folder_name)
    user = request.user
    mail_details = None
    if folder_name == 'inbox':
        print('test')
        mail_details = Mail.objects.filter(id=mail_id, to_user=user, folder_name=folder_name)
        mark_mail_read(mail_id, folder_name, user)
        print(mail_details)
    elif folder_name == 'sent':
        mail_details = Mail.objects.filter(id=mail_id, from_user=user, folder_name=folder_name)
    if mail_details:
        mail_details = list(mail_details.annotate(username=F('from_user__username'), user_email = F('from_user__email')).values('id', 'folder_name','user_email', 'username', 'subject', 'category', 'label', 'created_at', 'content'))
        mail_details = mail_details[0]
    return JsonResponse({'status': 'success', 'mail_details': mail_details})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_mail_folder_data(request):
    user = request.user
    mail_folders = list(Mail_Folder.objects.filter(user = user).values())
    return JsonResponse({'status': 'success', 'mail_folders': mail_folders})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mail_events(request):
    print(mail_id, folder_name)
    user = request.user
    mail_id = request.POST.get('mailId')
    folder_name = request.POST.get('folderName', None)
    is_read = request.POST.get('folderName', None)
    if mail_id and folder_name and is_read:
         mark_mail_read(mail_id,folder_name, user )
    return JsonResponse({'status': 'success'})
