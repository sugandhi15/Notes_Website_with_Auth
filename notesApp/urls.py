from django.urls import path
from .views import NotesViewSet
from rest_framework.routers import DefaultRouter
from .views import Register,ResetPassword,passwordResetToken,specificNote

router = DefaultRouter()
router.register(r'notes', NotesViewSet, basename='notes')

urlpatterns = [

    path('register/',Register,name="register"),
    path('note/<int:id>',specificNote,name="specificNote"),
    path('password/reset/',ResetPassword,name="resetPassword"),
    path('password/reset/<str:token>',passwordResetToken,name="resetPassword"),
    # path('pass/reset/',UserPassReset,name="passReset"),
]
urlpatterns += router.urls