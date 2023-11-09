from django.contrib import admin
from django.urls import path
from vcfapp.views import home
from vcfapp import views
from vcfapp.views import home, add_individual_data_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', home, name='home'),
    path('delete_variant/<str:id>/', views.delete_variant, name='delete_variant'),
    path('modify_variant/<str:id>/', views.modify_variant, name='modify_variant'),
    path('visual-summary/', views.visual_summary, name='visual-summary'),
    path('add-individual-var/', add_individual_data_view, name='add-individual-var')
]
