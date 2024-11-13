from django.urls import path
from signifyapp import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login_existing'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('edit-profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('display-records-above-10/', views.display_records_with_average_above_10, name='display_records_above_10'),
    path('', views.index, name='index'),
]