from django.urls import path
from .views import add_house
from . import views


urlpatterns = [
    path('login',views.rent_login),
    path('validate/<name>/<password>/<email>/<otp>',views.validate,name="validate"),
    path('logout',views.rent_logout),
    # -------------------------Admin--------
    path('admin_home',views.admin_home),
    path('add_house', add_house, name='add_house'),
    path('edit/<id>/', views.edit_house),  # Edit House
    path('delete/<id>/', views.delete_house),
    
    path('',views.user_home),
    path('register',views.register),
    # path('house_detail/<id>',views.house_detail),
    path('house_detail/<id>/', views.house_detail, name='house_detail'), 

     path('visit-request/<int:house_id>/',views.schedule_visit, name='schedule_visit'),
    path('admin/visit-requests/', views.manage_visit_requests, name='manage_visit_requests'),
    path('admin/visit-request/<int:visit_id>/<str:status>/', views.update_visit_status, name='update_visit_status'),
]
