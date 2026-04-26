from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from PIL import Image
import io
from django.core.files.base import ContentFile


def validate_file_size(file):
    max_size = 5 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError("File size must be under 5 MB.")

class Department(models.Model):
    name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class School(models.Model):
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name




class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    SESSION_CHOICES = [
        (f"{year}-{year+1}", f"{year}-{year+1}") for year in range(datetime.now().year, 1989, -1)
    ]

    HOMETOWN_CHOICES = [
        ('Bagerhat', 'Bagerhat'), ('Bandarban', 'Bandarban'), ('Barguna', 'Barguna'),
        ('Barisal', 'Barisal'), ('Bhola', 'Bhola'), ('Bogura', 'Bogura'),
        ('Brahmanbaria', 'Brahmanbaria'), ('Chandpur', 'Chandpur'), ('Chapainawabganj', 'Chapainawabganj'),
        ('Chattogram', 'Chattogram'), ('Chuadanga', 'Chuadanga'), ('Comilla', 'Comilla'),
        ('Coxs Bazar', "Cox's Bazar"), ('Dhaka', 'Dhaka'), ('Dinajpur', 'Dinajpur'),
        ('Faridpur', 'Faridpur'), ('Feni', 'Feni'), ('Gaibandha', 'Gaibandha'),
        ('Gazipur', 'Gazipur'), ('Gopalganj', 'Gopalganj'), ('Habiganj', 'Habiganj'),
        ('Jamalpur', 'Jamalpur'), ('Jessore', 'Jessore'), ('Jhalokati', 'Jhalokati'),
        ('Jhenaidah', 'Jhenaidah'), ('Joypurhat', 'Joypurhat'), ('Khagrachhari', 'Khagrachhari'),
        ('Khulna', 'Khulna'), ('Kishoreganj', 'Kishoreganj'), ('Kurigram', 'Kurigram'),
        ('Kushtia', 'Kushtia'), ('Lakshmipur', 'Lakshmipur'), ('Lalmonirhat', 'Lalmonirhat'),
        ('Madaripur', 'Madaripur'), ('Magura', 'Magura'), ('Manikganj', 'Manikganj'),
        ('Meherpur', 'Meherpur'), ('Moulvibazar', 'Moulvibazar'), ('Munshiganj', 'Munshiganj'),
        ('Mymensingh', 'Mymensingh'), ('Naogaon', 'Naogaon'), ('Narail', 'Narail'),
        ('Narayanganj', 'Narayanganj'), ('Narsingdi', 'Narsingdi'), ('Natore', 'Natore'),
        ('Netrokona', 'Netrokona'), ('Nilphamari', 'Nilphamari'), ('Noakhali', 'Noakhali'),
        ('Pabna', 'Pabna'), ('Panchagarh', 'Panchagarh'), ('Patuakhali', 'Patuakhali'),
        ('Pirojpur', 'Pirojpur'), ('Rajbari', 'Rajbari'), ('Rajshahi', 'Rajshahi'),
        ('Rangamati', 'Rangamati'), ('Rangpur', 'Rangpur'), ('Satkhira', 'Satkhira'),
        ('Shariatpur', 'Shariatpur'), ('Sherpur', 'Sherpur'), ('Sirajganj', 'Sirajganj'),
        ('Sunamganj', 'Sunamganj'), ('Sylhet', 'Sylhet'), ('Tangail', 'Tangail'),
        ('Thakurgaon', 'Thakurgaon'),
    ]

    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    social_profile = models.URLField(max_length=200, blank=True, null=True)
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True)
    school = models.ForeignKey('School', on_delete=models.SET_NULL, blank=True, null=True)
    hometown = models.CharField(max_length=50, choices=HOMETOWN_CHOICES, blank=True, null=True)

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    blood = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    session = models.CharField(max_length=20, choices=SESSION_CHOICES, blank=True, null=True)
    
    email_verified = models.BooleanField(default=False)
    
    student_proof = models.ImageField(
        upload_to='student_proofs/',
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        blank=True, null=True
    )
    
    def save(self, *args, **kwargs):
        if self.student_proof:
            MAX_IMAGE_SIZE = (1080, 1080)
            
            img = Image.open(self.student_proof)
            img = img.convert('RGB')  # Ensure RGB for WebP

            # Resize to max dimensions while keeping aspect ratio
            img.thumbnail(MAX_IMAGE_SIZE, Image.LANCZOS)

            # Save as WebP
            output = io.BytesIO()
            img.save(output, format='WEBP', quality=90)
            output.seek(0)

            # Replace original file with WebP version
            self.student_proof = ContentFile(
                output.read(),
                name=f"{self.student_proof.name.split('.')[0]}.webp"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    
















class ProfileVisit(models.Model):
    profile = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='visits_received', on_delete=models.CASCADE)
    visitor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='visits_made', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.visitor.username} visited {self.profile.username} at {self.timestamp}"

class PrimarySetting(models.Model):
    auto_approve = models.BooleanField(default=False)





