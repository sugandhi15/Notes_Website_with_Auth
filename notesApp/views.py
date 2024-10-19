from django.shortcuts import render
from rest_framework import viewsets
from .serializer import NotesSerializer
from .models import Notes
# from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
import json

# Create your views here.
class NotesViewSet(viewsets.ModelViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = NotesSerializer
    queryset = Notes.objects.all()  # Use this if you want to fetch all notes

    # OR (alternative):
    def get_queryset(self):
        # Customize this method to filter based on user or other conditions
        return Notes.objects.filter(user=self.request.user)

    # def get(self):
    #     return Notes.objects.filter(user=self.request.user)

    # def get(self, request):
    #     data = Notes.objects.filter(user = request)
    #     return Response(data)
    
    # queryset = Notes.objects.all()

@api_view(['POST'])
@permission_classes([AllowAny])
def Register(request):
    print(request.body)
    try:
        jsonData = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON format"}, status=400)
    
    username = jsonData.get('username')
    password = jsonData.get('password')

    if not username or not password:
        return Response({"error": "username and password are required"}, status=400)

    try:
        user = User.objects.create_user(username=username, password=password)
        return Response({"message": "User registered successfully"}, status=201)
    except IntegrityError:
        return Response({"error": "Username already exists"}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)