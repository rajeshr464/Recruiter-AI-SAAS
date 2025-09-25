# Dashboard API endpoint for current user info
from .models import *
from .serializers import *
from core.viewsets import TenantSafeViewSet
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from core.middleware import get_current_tenant


class TenantViewSet(TenantSafeViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

    
class ClientViewSet(TenantSafeViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class RecruiterViewSet(TenantSafeViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RecruiterAIViewSet(TenantSafeViewSet):
    queryset = RecruiterAI.objects.all()
    serializer_class = RecruiterAISerializer


class CandidateViewSet(TenantSafeViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer


class JobViewSet(TenantSafeViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class SubmissionViewSet(TenantSafeViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer


class InterviewViewSet(TenantSafeViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer


class OfferViewSet(TenantSafeViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer



class AILearningLogViewSet(TenantSafeViewSet):
    queryset = AILearningLog.objects.all()
    serializer_class = AILearningLogSerializer


# Placeholder viewsets for missing entities
class TaskViewSet(TenantSafeViewSet):
    queryset = Submission.objects.all()  # Using Submission as a placeholder
    serializer_class = SubmissionSerializer


class ReportViewSet(TenantSafeViewSet):
    queryset = AILearningLog.objects.all()  # Using AILearningLog as a placeholder
    serializer_class = AILearningLogSerializer


class SettingViewSet(TenantSafeViewSet):
    queryset = Tenant.objects.all()  # Using Tenant as a placeholder
    serializer_class = TenantSerializer


class HelpViewSet(TenantSafeViewSet):
    queryset = Tenant.objects.all()  # Using Tenant as a placeholder
    serializer_class = TenantSerializer


# Dashboard page view
class DashboardView(View):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect("/login/")
        context = {
            "user_name": getattr(user, "name", ""),
            "user_email": getattr(user, "email", ""),
            "user_tenant": getattr(user.tenant, "name", "") if getattr(user, "tenant", None) else ""
        }
        return render(request, "dashboard.html", context)


# Login page view
class LoginView(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        from django.contrib.auth import authenticate, login
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/dashboard/")
        else:
            return render(request, "login.html", {"error": "Invalid credentials. Please try again."})

# Candidate intake form view
class CandidateIntakeView(View):
    def get(self, request):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return HttpResponseRedirect("/login/")
        
        context = {}
        return render(request, "candidate_intake_form.html", context)
    
    def post(self, request):
        from django.shortcuts import redirect
        from django.contrib import messages
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import os
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return HttpResponseRedirect("/login/")
        
        # Get tenant from authenticated user
        tenant = request.user.tenant
        if not tenant:
            messages.error(request, "User must be associated with a tenant.")
            return render(request, "candidate_intake_form.html", {})
        
        # Get form data
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        location = request.POST.get("location")
        visa_status = request.POST.get("visa_status")
        experience_years = request.POST.get("experience_years")
        resume = request.FILES.get("resume")
        
        # Get skills as comma-separated string and convert to JSON
        skills_text = request.POST.get("skills", "")
        skills_list = [skill.strip() for skill in skills_text.split(",") if skill.strip()]
        skills = {skill: 1 for skill in skills_list}  # Simple dict with skill names as keys
        
        # Validate required fields
        if not name or not email:
            messages.error(request, "Name and email are required.")
            return render(request, "candidate_intake_form.html", {})
        
        # Create candidate
        try:
            candidate = Candidate.objects.create(
                tenant=tenant,
                name=name,
                email=email,
                phone=phone or "",
                location=location or "",
                visa_status=visa_status or "",
                experience_years=int(experience_years) if experience_years else 0,
                skills=skills,
                resume_url=""  # Will be updated after file upload
            )
            
            # Handle resume upload if provided
            if resume:
                # Create tenant-specific directory if it doesn't exist
                tenant_dir = f"resumes/tenant_{tenant.id}"
                path = default_storage.save(
                    f"{tenant_dir}/{resume.name}",
                    ContentFile(resume.read())
                )
                candidate.resume_url = default_storage.url(path)
                candidate.save()
            
            messages.success(request, "Candidate added successfully.")
            return redirect("dashboard")
        except Exception as e:
            messages.error(request, f"Error adding candidate: {str(e)}")
            return render(request, "candidate_intake_form.html", {})


# Resume parsing view
class ParseResumeView(View):
    def post(self, request):
        from django.http import JsonResponse
        from ai_engine.utils.resume_parser import parse_resume
        import os
        import tempfile
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)
        
        resume = request.FILES.get("resume")
        if not resume:
            return JsonResponse({"error": "No resume file provided"}, status=400)
        
        # Create a temporary file to store the uploaded resume
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume.name)[1]) as temp_file:
                temp_file.write(resume.read())
                temp_file_path = temp_file.name
            
            # Determine file type
            file_extension = os.path.splitext(resume.name)[1].lower().replace('.', '')
            
            # Parse the resume
            parsed_data = parse_resume(temp_file_path, file_extension)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            if parsed_data:
                return JsonResponse({"success": True, "data": parsed_data})
            else:
                return JsonResponse({"error": "Failed to parse resume"}, status=400)
                
        except Exception as e:
            # Clean up temporary file if it exists
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
            return JsonResponse({"error": f"Error processing resume: {str(e)}"}, status=500)
        
# candidates List view
class CandidateListView(View):
    """
    Multi-tenant candidate list view for dashboards.
    Only shows candidates for the current tenant.
    """
    def get(self, request):
        tenant = get_current_tenant()
        if not tenant:
            # Optional: Show an error or redirect for unauthenticated/no-tenant requests
            return render(request, "error.html", {"message": "Tenant not found"})
        # Filter candidates for this tenant only
        candidates = Candidate.objects.filter(tenant=tenant)
        context = {"candidates": candidates}
        return render(request, "candidate_list.html", context)
