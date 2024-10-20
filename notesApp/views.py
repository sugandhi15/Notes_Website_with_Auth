# from django.shortcuts import render
from rest_framework import viewsets
from .serializer import NotesSerializer
from .models import Notes
from rest_framework.views import APIView
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

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist



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
        
        elif request.method == 'PUT':
            serializer = NotesSerializer(note, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)


        elif request.method == 'DELETE':
            note.delete()
            return Response({'message': 'Note deleted successfully'})
        
    except Exception as e:
        return Response({'message':e})





# viewset for notes
class NotesViewSet(viewsets.ModelViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = NotesSerializer
    queryset = Notes.objects.all() 

    def get_queryset(self):
        # to get user specific notes
        return Notes.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        try:
            #  to create a link with serialiser and create a instance
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                "msg":e
            })
    


#  To register a new user
@api_view(['POST'])
@permission_classes([AllowAny])
def Register(request):
    try:
        jsonData = json.loads(request.body.decode('utf-8'))
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
    
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User with this email does not exist."}, status=404)
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
    
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User with this email does not exist."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    


#  to change password from link through email
@api_view(['POST'])
def UserPassReset(request):
    permission_classes = [IsAuthenticated]

    user = request.user
    newPass = request.POST['password']

    user.set_password(newPass)
    user.save()
    user_data = {
        'username': user.username,
        'email': user.email,
        'password':user.password,
    }
    return Response(user_data)