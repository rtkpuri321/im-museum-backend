"""immuseum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path



urlpatterns = [
    path('register/', UserRegister.as_view()),
    path('login/',LoginAPIView.as_view()),
    path('user-details/',UserDataAPIView.as_view()),
    path('add-image/',AddUserImageView.as_view()),
    path('get-image/<int:user_id>/<image_name>/',GetImage.as_view())
]

# Add this line to serve static files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
