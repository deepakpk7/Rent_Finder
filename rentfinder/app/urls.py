from django.urls import path
from .views import add_house
from . import views


urlpatterns = [
    path('login',views.rent_login),
    # path('validate/<name>/<password>/<email>/<otp>',views.validate_otp,name="validate"),
    path('validate-otp/',views.validate_otp, name='validate_otp'),

    path('logout',views.rent_logout),
    # -------------------------Admin--------
    path('admin_home',views.admin_home),
    path('add_house', add_house, name='add_house'),
    path('edit/<id>/', views.edit_house),  
    path('delete/<id>/', views.delete_house),
    path('user_post',views.user_post),
    
    
    
    path('',views.user_home),
    path('register',views.register),
    path('house_detail/<id>/', views.house_detail, name='house_detail'), 
    path('visit/<id>',views.visit),
    path('profile',views.profile),
    path('update_profile',views.update_profile),
    path('contact',views.contact),
    path('about',views.about),
    path('post_property',views.post_property),

    # path('visit-request/<int:house_id>/',views.schedule_visit, name='schedule_visit'),
    path('visit_requests', views.manage_visit_requests, name='manage_visit_requests'),
    path('visit-request/<id>/<str:status>/', views.update_visit_status, name='update_visit_status'),
]
