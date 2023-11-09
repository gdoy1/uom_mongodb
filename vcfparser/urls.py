from django.contrib import admin
from django.urls import path, include
from vcfapp.views import home, upload
from vcfapp import views
from vcfapp.views import home, add_individual_data_view, upload

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', home, name='home'),
    path('delete_variant/<str:id>/', views.delete_variant, name='delete_variant'),
    path('modify_variant/<str:id>/', views.modify_variant, name='modify_variant'),
    path('visual-summary/', views.visual_summary, name='visual-summary'),
    path('visual-summary-query/<start_range>/<end_range>/', views.visual_summary_query, name='visual-summary-query'),
    path('add-individual-var/', add_individual_data_view, name='add-individual-var'),
    path('upload/', upload, name='upload'),
]
