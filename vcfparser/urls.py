from django.contrib import admin
from django.urls import path
from vcfapp.views import home
from vcfapp import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', home, name='home'),
    path('delete_variant/<str:id>/', views.delete_variant, name='delete_variant'),
    path('modify_variant/<str:id>/', views.modify_variant, name='modify_variant'),
    path('visual-summary/', views.visual_summary, name='visual-summary'),

]
