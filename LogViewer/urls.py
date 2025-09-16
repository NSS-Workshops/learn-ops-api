from django.urls import path
from . import views

app_name = 'logviewer' # Namespace for the app's URLs

urlpatterns = [
    path('', views.log_list, name='log_list'),
    # Add more paths for filtering, detail views, etc. later
]