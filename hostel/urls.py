from django.urls import path
from hostel import views
from .views import pay_fee_summary, pay_fee,view_meals_user,room_availability,view_attendance_user,admin_view_attendance


urlpatterns = [
    path('', views.home, name='root'),       
    path('home', views.home, name='home'),
    path('about', views.about, name='about'),
    path('register', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout_view', views.logout_view, name='logout_view'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('official_login/', views.official_login_view, name='official_login'),
    path('warden_login/', views.warden_login_view, name='warden_login'),
    path('staff_login/', views.staff_login_view, name='staff_login'),
    # ADMIN DASHBOARD ROUTES
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('view_payments/', views.view_payments, name='view_payments'),
    path('admin/leave-requests/', views.admin_view_leave_requests, name='admin_view_leave_requests'),
    path('admin/leave-requests/update/<int:pk>/', views.update_leave_request_status, name='update_leave_request_status'),
    path('add_staff_view/', views.add_staff_view, name='add_staff'),
    path('admin_logout/', views.admin_logout_view, name='admin_logout_view'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff_logout/', views.staff_logout, name='staff_logout'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('view_complaints_staff/', views.view_complaints_staff, name='view_complaints_staff'),
    path('view_maintenance_staff/', views.view_maintenance_staff, name='view_maintenance_staff'),
    path('allocate_rooms/', views.allocate_rooms, name='allocate_rooms'),
    path('add_mess_details/', views.add_mess_details, name='add_mess_details'),
    path('leave_request/', views.leave_request, name='leave_request'),
    path('complaint_register/', views.complaint_register, name='complaint_register'),
    path('pay_fee/', views.pay_fee, name='pay_fee'),
    path('staff/complaints/', views.view_complaints_staff, name='view_complaints_staff'),
    path('staff/complaints/update/<int:complaint_id>/', views.update_complaint_status, name='update_complaint_status'),
    path('staff/complaints/update/<int:complaint_id>/', views.update_complaint_status, name='update_complaint_status'),
    path('staff/leave-requests/', views.view_leave_requests_staff, name='view_leave_requests_staff'),
    path('leave-requests/update/<int:pk>/', views.update_leave_request_status_staff, name='update_leave_request_status_staff'),
    path('staff/allocate-rooms/', views.allocate_rooms, name='allocate_rooms'),
    path('staff/attendance/', views.mark_attendance, name='mark_attendance'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('view-attendance/', views.view_all_attendance, name='view_attendance'),
    path('meals/', views.view_or_add_meals, name='view_or_add_meals'),
    path('meals/update/<int:meal_id>/', views.update_meal, name='update_meal'),
    path('pay-fee-summary/', pay_fee_summary, name='pay_fee_summary'),
    path('view-meals/', view_meals_user, name='view_meals'),
    path('room-availability/', room_availability, name='room_availability'),
    path('view-attendance-user/', view_attendance_user, name='view_attendance_user'),
    path('custom-admin/complaints/', views.admin_view_complaints, name='admin_view_complaints'),
    path('custom-admin/complaints/update/<int:complaint_id>/', views.admin_update_complaint_status, name='admin_update_complaint_status'),
    path('custom-admin/attendance/', views.admin_view_attendance, name='admin_view_attendance'),
    path('leave-requests/', views.admin_view_leave_requests, name='admin_view_leave_requests'),
    path('leave-requests/update/<int:pk>/', views.update_leave_request_status, name='update_leave_request_status')


]

