
from django.db import models
from django.contrib.auth.models import AbstractUser


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    subscription_plan = models.CharField(max_length=20, choices=[("Free","Free"),("Pro","Pro"),("Enterprise","Enterprise")])
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[("Active","Active"),("Suspended","Suspended")])


    def __str__(self):
        return self.name


from django.contrib.auth.base_user import BaseUserManager

# Custom user manager for recruiters
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


# Custom user model for recruiters
class User(AbstractUser):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="users", null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    # Password is handled by AbstractUser (use set_password and check_password)
    username = None  # Remove username field
    USERNAME_FIELD = 'email'  # Use email for authentication
    REQUIRED_FIELDS = ['name']  # Name required for createsuperuser

    objects = UserManager()



class Client(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="clients")
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    msa_signed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="candidates")
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    visa_status = models.CharField(max_length=50)
    skills = models.JSONField(default=dict)
    experience_years = models.IntegerField()
    resume_url = models.URLField()
    ai_learning_profile = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="jobs")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    pay_rate = models.DecimalField(max_digits=10, decimal_places=2)
    employment_type = models.CharField(max_length=50, choices=[("W2","W2"),("C2C","C2C"),("Full-time","Full-time")])
    skills_required = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=[("Open","Open"),("Closed","Closed"),("On Hold","On Hold")])
    ai_learning_notes = models.JSONField(default=dict)

    def __str__(self):
        return self.title


class RecruiterAI(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="recruiter_ais")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Submission(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="submissions")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="submissions")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="submissions")
    status = models.CharField(max_length=20, choices=[("Submitted","Submitted"),("Rejected","Rejected"),("Interview","Interview"),("Offer","Offer"),("Hired","Hired")])
    submitted_on = models.DateTimeField(auto_now_add=True)
    # recruiter field removed (was ForeignKey to Recruiter)
    ai = models.ForeignKey(RecruiterAI, on_delete=models.SET_NULL, null=True, blank=True, related_name="submissions")
    created_by = models.CharField(max_length=20, choices=[("AI","AI"),("Recruiter","Recruiter")])
    feedback = models.JSONField(default=dict, blank=True, null=True)
    ai_decision_log = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"Submission {self.id} - {self.candidate.name} for {self.job.title}"


class Interview(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="interviews")
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="interviews")
    scheduled_on = models.DateTimeField()
    type = models.CharField(max_length=20, choices=[("L1","L1"),("L2","L2"),("Client","Client"),("HR","HR")])
    status = models.CharField(max_length=20, choices=[("Scheduled","Scheduled"),("Completed","Completed"),("Cancelled","Cancelled"),("No-Show","No-Show")])
    notes = models.TextField(blank=True, null=True)
    ai_learning_notes = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"Interview {self.id} - {self.submission}"


class Offer(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="offers")
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="offer")
    offered_rate = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    status = models.CharField(max_length=20, choices=[("Accepted","Accepted"),("Rejected","Rejected"),("Pending","Pending")])
    ai_learning_notes = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"Offer {self.id} for {self.submission}"


class AILearningLog(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="ai_learning_logs")
    ai = models.ForeignKey(RecruiterAI, on_delete=models.SET_NULL, null=True, blank=True, related_name="learning_logs")
    entity_type = models.CharField(max_length=50, choices=[("Candidate","Candidate"),("Job","Job"),("Submission","Submission"),("Interview","Interview"),("Offer","Offer")])
    entity_id = models.UUIDField()
    action = models.CharField(max_length=255)
    outcome = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    learning_vector = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"Log {self.id} - {self.action}"
