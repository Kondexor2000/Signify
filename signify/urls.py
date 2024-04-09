from django.urls import path
from signifyapp import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login_existing'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('edit-profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('add-invoice/', views.AddInvoiceView.as_view(), name='add_invoice'),
    path('read-invoices/', views.read_invoices, name='read_invoices'),
    path('read-invoices-by-admin/', views.read_invoices_by_admin, name='read_invoices_by_admin'),
    path('update-invoice/<int:pk>/', views.UpdateInvoiceView.as_view(), name='update_invoice'),
    path('delete-invoice/<int:pk>/', views.DeleteInvoiceView.as_view(), name='delete_invoice'),
    path('check-payment-deadline/', views.check_payment_deadline, name='check_payment_deadline'),
    path('display-records-above-10/', views.display_records_with_average_above_10, name='display_records_above_10'),
    path('', views.index, name='index'),
]