from django.shortcuts import render, redirect,get_object_or_404
from .models import Login, UserInfo,FeePayment,Complaint,LeaveRequest,Room, RoomAllocation,Attendance,MessDetail,DAYS_OF_WEEK
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from datetime import date
from django.utils.timezone import now
import re

# Create your views here.
def home(request):
    return render(request, 'home.html')
def register(request):
    if request.method == 'POST':
        fullname = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        password = request.POST['password']

        # Check if username/email already exists
        if Login.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        login_obj = Login.objects.create(
            username=email,
            password=make_password(password),  # hash password
        )
        UserInfo.objects.create(
            login=login_obj,
            fullname=fullname,
            email=email,
            phone_number=phone,
            address=address
        )
        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, 'register.html')


def about(request):
     return render(request,'about.html')


# login_view
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Login

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # 1️⃣ Try Django superuser
        try:
            auth_user = User.objects.get(email=email)
            # Use username from auth_user
            user = authenticate(request, username=auth_user.username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('/admin/')
                return redirect('dashboard')
        except User.DoesNotExist:
            pass  # move to custom Login

        # 2️⃣ Try custom Login
        try:
            custom_user = Login.objects.get(username=email)
        except Login.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html')

        # check hashed password
        from django.contrib.auth.hashers import check_password
        if check_password(password, custom_user.password):
            request.session['custom_user_id'] = custom_user.id
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html')

    return render(request, 'login.html')


def logout_view(request):
    # ✅ Log out Django authenticated users (warden/staff)
    logout(request)

    # ✅ Also clear any custom sessions (for normal users)
    request.session.flush()

    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

def dashboard(request):
    return render(request, "dashboard.html")

def official_login_view(request):
    return render(request, 'official_login.html')
def warden_login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Warden login successful.")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid warden credentials or unauthorized access.")
            return redirect('official_login')  # stay on same page for retry

    return render(request, 'warden_login.html')

def staff_login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and not user.is_superuser:  # or condition for staff
            login(request, user)
            messages.success(request, "Staff login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid staff credentials.")
    return render(request, 'staff_login.html')


def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

def view_payments(request):
    payments = FeePayment.objects.filter(status='Paid').order_by('-payment_date')
    return render(request, 'admin/view_payments.html', {'payments': payments})


def admin_view_complaints(request):
    complaints = Complaint.objects.all().order_by('-date_submitted')
    return render(request, 'admin/admin_view_complaints.html', {'complaints': complaints})

# Update complaint status (for admin)
def admin_update_complaint_status(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        complaint.status = new_status
        complaint.save()

    return redirect('admin/admin_view_complaints')

def admin_view_attendance(request):
    attendances = Attendance.objects.select_related('student').order_by('-date')
    return render(request, 'admin/admin_view_attendance.html', {'attendances': attendances})

def admin_view_leave_requests(request):
    leave_requests = LeaveRequest.objects.select_related('user').order_by('-date_applied')
    return render(request, 'admin/admin_view_leave_requests.html', {'leave_requests': leave_requests})

def update_leave_request_status_staff(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if request.method == 'POST':
        print("POST received:", request.POST)
        status = request.POST.get('status')
        print("New status:", status)
        if status in ['Pending', 'Approved', 'Rejected']:
            leave_request.status = status
            leave_request.save()
            messages.success(request, "Leave request status updated.")
        else:
            messages.error(request, "Invalid status.")
    else:
        messages.error(request, "Invalid request method.")
    
    return redirect('staff_dashboard')

def admin_logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully, Warden.")
    return redirect('official_login')

def add_staff_view(request):
    if request.method == "POST":
        fullname = request.POST['fullname']
        phone = request.POST['phone']
        address = request.POST['address']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        # Check duplicates
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists in Django auth.")
            return render(request, 'admin/add_staff_form.html')

        if Login.objects.filter(username=email).exists():
            messages.error(request, "Email already exists in Login table.")
            return render(request, 'admin/add_staff_form.html')

        # Create Django User
        User.objects.create_user(username=username, password=password, is_staff=True)

        # Create custom Login
        login_obj = Login.objects.create(
            username=email,
            password=make_password(password),
            usertype="staff",
            status="Approved"
        )

        # Create UserInfo
        UserInfo.objects.create(
            login=login_obj,
            fullname=fullname,
            email=email,
            phone_number=phone,
            address=address
        )

        messages.success(request, "Hostel staff added successfully!")
        return render(request, 'admin/add_staff_form.html')

    return render(request, 'admin/add_staff_form.html')

def staff_login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate using Django's built-in User model
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff and not user.is_superuser:
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Staff login successful.")
            return redirect('staff_dashboard')  # or staff dashboard page
        else:
            messages.error(request, "Invalid staff credentials.")

    return render(request, 'staff_login.html')
@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser)
def staff_dashboard(request):
    return render(request, 'staff/staff_dashboard.html')
# ✅ Staff Logout
def staff_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('staff_login')

# ✅ Placeholder views for buttons (you can expand later)
def mark_attendance(request):
    return render(request, 'staff/mark_attendance.html')

def view_complaints_staff(request):
    return render(request, 'staff/view_complaints_staff.html')

def view_maintenance_staff(request):
    return render(request, 'staff/view_maintenance_staff.html')

def allocate_rooms(request):
    return render(request, 'staff/allocate_rooms.html')

def add_mess_details(request):
    return render(request, 'staff/add_mess_details.html')

def leave_request(request):
    if 'custom_user_id' not in request.session:
        return redirect('login')  # user not logged in

    user_id = request.session['custom_user_id']
    user = Login.objects.get(id=user_id)

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        if start_date and end_date and reason:
            LeaveRequest.objects.create(
                user=user,
                start_date=start_date,
                end_date=end_date,
                reason=reason
            )
            messages.success(request, "Leave request submitted successfully ✅")
            return redirect('leave_request')
        else:
            messages.error(request, "Please fill all fields!")

    # Show user's previous leave requests
    leaves = LeaveRequest.objects.filter(user=user).order_by('-date_applied')
    return render(request, 'users/leave_request.html', {'leaves': leaves})

def complaint_register(request):
    if 'custom_user_id' not in request.session:
        return redirect('login')

    user_id = request.session['custom_user_id']
    user = Login.objects.get(id=user_id)

    if request.method == 'POST':
        subject = request.POST.get('subject')
        description = request.POST.get('description')

        if subject and description:
            Complaint.objects.create(user=user, subject=subject, description=description)
            messages.success(request, "Complaint submitted successfully ✅")
            return redirect('complaint_register')
        else:
            messages.error(request, "Please fill out all fields.")

    complaints = Complaint.objects.filter(user=user).order_by('-date_submitted')
    return render(request, 'users/complaint_register.html', {'complaints': complaints})

def pay_fee(request):
    if 'custom_user_id' not in request.session:
        return redirect('login')

    user_id = request.session['custom_user_id']
    user = Login.objects.get(id=user_id)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')

        if amount:
            FeePayment.objects.create(
                user=user,
                amount=amount,
                status="Paid",
                due_date=due_date or timezone.now().date(),
                remarks="Payment successful"
            )
            messages.success(request, "Fee payment successful ✅")
            return redirect('pay_fee')
        else:
            messages.error(request, "Please enter a valid amount.")

    # Fetch payment history
    payments = FeePayment.objects.filter(user=user).order_by('-payment_date')
    return render(request, 'users/pay_fee.html', {'payments': payments})

def is_staff_user(user):
    return user.is_authenticated and user.is_staff and not user.is_superuser

def view_complaints_staff(request):
    complaints = Complaint.objects.select_related('user').all()
    return render(request, 'staff/view_complaints_staff.html', {'complaints': complaints})

def update_complaint_status(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            complaint.status = new_status
            complaint.save()
            messages.success(request, f'Complaint status updated to "{new_status}".')
    return redirect('view_complaints_staff')

def view_leave_requests_staff(request):
    leave_requests = LeaveRequest.objects.all().order_by('-date_applied')
    return render(request, 'staff/view_leave_requests_staff.html', {'leave_requests': leave_requests})

def update_leave_request_status(request, leave_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    new_status = request.POST.get('status')

    if new_status in ['Pending', 'Approved', 'Rejected']:
        leave_request.status = new_status
        leave_request.save()
    return redirect('view_leave_requests_staff')

def allocate_rooms(request):
    students = Login.objects.filter(usertype='user')  # Or your student filter
    rooms = Room.objects.all()

    if request.method == 'POST':
        student_id = request.POST.get('student')
        room_id = request.POST.get('room')

        student = get_object_or_404(Login, id=student_id)
        room = get_object_or_404(Room, id=room_id)

        # Optional: Check room capacity (example)
        allocated_count = RoomAllocation.objects.filter(room=room).count()
        if allocated_count >= room.capacity:
            messages.error(request, f"Room {room.room_number} is full!")
        else:
            # Remove previous allocation if exists
            RoomAllocation.objects.filter(student=student).delete()
            # Allocate room
            RoomAllocation.objects.create(student=student, room=room)
            messages.success(request, f"Allocated room {room.room_number} to {student.username}")

        return redirect('allocate_rooms')

    # For showing current allocations
    allocations = RoomAllocation.objects.select_related('student', 'room')

    context = {
        'students': students,
        'rooms': rooms,
        'allocations': allocations,
    }
    return render(request, 'staff/allocate_rooms.html', context)

def mark_attendance(request):
    students = Login.objects.filter(usertype='user')

    if request.method == 'POST':
        selected_date = request.POST.get('date')
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            Attendance.objects.update_or_create(
                student=student, date=selected_date,
                defaults={'status': status}
            )
        messages.success(request, "Attendance marked successfully.")
        return redirect('mark_attendance')

    return render(request, 'staff/mark_attendance.html', {'students': students})

def view_all_attendance(request):
    all_attendance = Attendance.objects.select_related('student').order_by('-date')
    return render(request, 'staff/view_attendance.html', {'attendances': all_attendance})

def view_or_add_meals(request):
    meals = MessDetail.objects.all().order_by('id')
    if meals.count() < 7:
        # Show form to add meals for the week
        if request.method == 'POST':
            for day in DAYS_OF_WEEK:
                MessDetail.objects.create(
                    day=day[0],
                    breakfast=request.POST.get(f'breakfast_{day[0]}'),
                    lunch=request.POST.get(f'lunch_{day[0]}'),
                    dinner=request.POST.get(f'dinner_{day[0]}'),
                )
            messages.success(request, "Meals for the week added successfully.")
            return redirect('view_or_add_meals')
        return render(request, 'staff/add_meals.html', {'days': DAYS_OF_WEEK})
    
    # Show existing meals with update option
    return render(request, 'staff/view_meals.html', {'meals': meals})


# Update a specific day's meals
def update_meal(request, meal_id):
    meal = get_object_or_404(MessDetail, id=meal_id)

    if request.method == 'POST':
        meal.breakfast = request.POST.get('breakfast')
        meal.lunch = request.POST.get('lunch')
        meal.dinner = request.POST.get('dinner')
        meal.save()
        messages.success(request, f"{meal.day} meals updated successfully.")
        return redirect('view_or_add_meals')

    return render(request, 'staff/update_meal.html', {'meal': meal})



def pay_fee_summary(request):
    if 'custom_user_id' not in request.session:
        return redirect('login')

    user_id = request.session['custom_user_id']
    user = Login.objects.get(id=user_id)
    today = now().date()
    current_month = today.month
    current_year = today.year

    attendance_records = Attendance.objects.filter(
        student=user,
        date__year=current_year,
        date__month=current_month,
        status='Present'
    )
    days_present = attendance_records.count()

    if request.method == 'POST':
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')
        if not amount:
            messages.error(request, "Please enter the amount to pay.")
        else:
            FeePayment.objects.create(
                user=user,
                amount=amount,
                status='Paid',
                due_date=due_date if due_date else None,
                remarks=f"Paid for {current_month}/{current_year}"
            )
            messages.success(request, "Fee paid successfully!")
            return redirect('pay_fee_summary')

    # Fetch previous payments to show in the summary page
    payments = FeePayment.objects.filter(user=user).order_by('-payment_date')

    context = {
        'days_present': days_present,
        'current_month': current_month,
        'current_year': current_year,
        'payments': payments,
    }
    return render(request, 'pay_fee_summary.html', context)

def view_meals_user(request):
    meals = MessDetail.objects.all().order_by('id')
    return render(request, 'users/view_meals_user.html', {'meals': meals})

def room_availability(request):
    allocations = RoomAllocation.objects.select_related('room', 'student').all()

    # Rooms that have been allocated (room ids)
    allocated_room_ids = allocations.values_list('room_id', flat=True)

    # Rooms not allocated
    remaining_rooms = Room.objects.exclude(id__in=allocated_room_ids)

    context = {
        'allocations': allocations,
        'remaining_rooms': remaining_rooms,
    }
    return render(request, 'users/room_availability.html', context)

def view_attendance_user(request):
    # Fetch attendance records, order by date descending
    attendance_records = Attendance.objects.select_related('student').order_by('-date')
    
    context = {
        'attendance_records': attendance_records,
    }
    return render(request, 'users/view_attendance_user.html', context)