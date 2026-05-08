from django.db import models

class Login(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    usertype = models.CharField(max_length=20, default="user")
    status = models.CharField(max_length=20, default="Approved")

class UserInfo(models.Model):
    login = models.ForeignKey(Login, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

class Complaint(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=50, default="Pending")
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject}"
    
class LeaveRequest(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default="Pending")
    date_applied = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.start_date} - {self.end_date})"
    
class FeePayment(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending')  # Pending / Paid
    payment_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.status} - ₹{self.amount}"
    
class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField(default=1)
    # Other fields like block/floor if needed

    def __str__(self):
        return self.room_number

class RoomAllocation(models.Model):
    student = models.ForeignKey(Login, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date_allocated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} -> {self.room.room_number}"
    
# models.py
class Attendance(models.Model):
    student = models.ForeignKey(Login, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.status}"

DAYS_OF_WEEK = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
]

class MessDetail(models.Model):
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK, unique=True)
    breakfast = models.TextField()
    lunch = models.TextField()
    dinner = models.TextField()

    def __str__(self):
        return self.day