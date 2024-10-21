# from django.shortcuts import render
from rest_framework import viewsets
from .serializer import NotesSerializer
from .models import Notes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
import json
from django.template.loader import render_to_string
from django.contrib.auth import login 
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.http import JsonResponse
# from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from social_django.utils import load_strategy, load_backend



# to get perform operations on note by specific id
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def specificNote(request,id):
    try:
        note = Notes.objects.get(id=id, user=request.user)
        # accesing specific note by id
        if request.method == 'GET':
            notes = Notes.objects.filter(id = id)
            return Response(notes)
        
        if request.method == 'PUT':
            try:
                data = request.data
                note = Notes.objects.get(id=id)
                serializer = NotesSerializer(instance=note, data=data)
                # serializer = NotesSerializer(note, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors)
            except Exception as e:
                return Response({
                    "msg":e
                })

        if request.method == 'DELETE':
            try:
                Notes.objects.get(id=id).delete()
                return Response({
                    'status': True,
                    'message': ' Note deleted successfully.'
                })
            except Exception as e:
                return Response({
                        'status': False,
                        'message':e
                    })
        
    except Exception as e:
        return Response({'message':e})




@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def NotesEndpt(request):
    try:
        note = Notes.objects.get(user=request.user)
        
        if request.method == 'GET':
            notes = Notes.objects.filter(user = request.user)
            return Response(notes)
        
        if request.method == 'POST':
            try:
                serializer = NotesSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save(user=request.user) 
                    return Response({
                        "message": "Note created successfully!",
                        "data": serializer.data
                    })
                
                return Response({
                    "errors": serializer.errors
                })
            except Exception as e:
                return Response({
                    "msg":e
                })

        if request.method == 'DELETE':
            try:
                Notes.objects.filter(user=request.user).delete()
                return Response({
                    'status': True,
                    'message': ' Note deleted successfully.'
                })
            except Exception as e:
                return Response({
                        'status': False,
                        'message':e
                    })
        
    except Exception as e:
        return Response({'message':e})



        

    def destroy_queryset(self, request, *args, **kwargs):
        try:
            Notes.objects.filter(user=request.user).delete()  
            return Response({
                'status': True,
                'message': 'All Notes deleted successfully.'
            })
        except Exception as e:
            return Response({
                "msg":e
            })



#  To register a new user
@api_view(['POST'])
@permission_classes([AllowAny])
def Register(request):
    try:
        jsonData = request.data
        print(json)
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON format"}, status=400)
    
    username = jsonData.get('username')
    password = jsonData.get('password')
    email = jsonData.get('email')

    if not username or not password or not email:
        return Response({"error": "username and password are required"}, status=400)

    try:
        user = User.objects.create_user(username=username, password=password , email =  email)
        return Response({"message": "User registered successfully"}, status=201)
    except IntegrityError:
        return Response({"error": "Username already exists"}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    


# To reset password without token
@api_view(['POST'])
@permission_classes([AllowAny])
def ResetPassword(request):
    email = request.data.get('email')

    if not email:
        return JsonResponse({"error": "Email is required."}, status=400)

    try:
        user = User.objects.get(email=email)
        password_reset_link = "http://localhost:8000/pass/reset/"
        subject = "Password Reset Requested"
        message = render_to_string('reset.html', {
            'password_reset_link': password_reset_link,
            'username': user.username,
        })

        send_mail(subject, message, 'sugandhibansal26@gmail.com', [email])
        return JsonResponse({"message": "Password reset link sent."}, status=200)
    
    # except ObjectDoesNotExist:
    #     return JsonResponse({"error": "User with this email does not exist."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    


# Reset Password with token
def passwordResetToken(request,token):
    email = request.data.get('email')

    if not email:
        return JsonResponse({"error": "Email is required."}, status=400)

    try:
        user = User.objects.get(email=email)
        password_reset_link = f"http://localhost:8000/pass/reset/{token}"

        subject = "Password Reset Requested"
        message = render_to_string('reset.html', {
            'password_reset_link': password_reset_link,
            'username': user.username,
        })

        send_mail(subject, message, 'sugandhibansal26@gmail.com', [email])
        return JsonResponse({"message": "Password reset link sent."}, status=200)
    
    # except ObjectDoesNotExist:
    #     return JsonResponse({"error": "User with this email does not exist."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    


# #  to change password from link through email
@api_view(['POST'])
def UserPassReset(request):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    username = request.data.get('username')
    new_password = request.data.get('password')

    try:
        user = User.objects.get(username=username) 
        user.set_password(new_password) 
        user.save()  
        return Response({'message': 'Password updated successfully'})
    except Exception as e:
        return Response({
            'error': e
        })

def google_login(request):
    strategy = load_strategy(request)
    backend = load_backend(strategy=strategy, name='google-oauth2', redirect_uri=None)
    return redirect(backend.auth_url())

def google_callback(request):
    # Get the logged-in user's social account info from Django Allauth
    user = request.user

    strategy = load_strategy(request)
    backend = load_backend(strategy=strategy, name='google-oauth2', redirect_uri=None)
    
    # Complete the authentication
    user = backend.do_auth(request.GET.get('code'))
    
    if user and user.is_active:
        login(request, user)  # Log the user in

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    else:
        return Response({"error": "Authentication failed"}, status=400)
    
@api_view(['GET'])
def FetchAllNotes(request):
    try:
        notes = Notes.objects.all()
        serializer = NotesSerializer(notes, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            "msg":e
        })
    
