from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('docs/', include('apps.documentos.urls')),
    path('chatbot/', include('apps.asistente.urls')),
]
