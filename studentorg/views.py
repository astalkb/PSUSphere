from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from studentorg.models import Organization, OrgMember, Student, College, Program
from studentorg.forms import OrganizationForm, OrgMemberForm, StudentForm, CollegeForm, ProgramForm
from django.urls import reverse_lazy 
from django.utils.decorators import method_decorator 
from django.contrib.auth.decorators import login_required 
from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Q 

@method_decorator(login_required, name='dispatch')
class OrganizationList(ListView):
     model = Organization
     context_object_name = 'organization'
     template_name = 'organization/org_list.html'
     paginate_by = 5

class HomePageView(ListView):
     model = Organization
     context_object_name = 'home'
     template_name = "home.html"
     paginate_by = 5 

     def get_queryset(self, *args, **kwargs):
          qs = super().get_queryset(*args, **kwargs)
          if self.request.GET.get("q") != None:
               query = self.request.GET.get('q')
               qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query))
          return qs

class OrganizationCreateView(CreateView):
     model = Organization
     form_class = OrganizationForm
     template_name = 'organization/org_add.html'
     success_url = reverse_lazy('organization-list')

class OrganizationUpdateView(UpdateView):
     model = Organization
     form_class = OrganizationForm
     template_name = 'organization/org_edit.html' 
     success_url = reverse_lazy('organization-list')

class OrganizationDeleteView(DeleteView):
     model = Organization
     template_name = 'organization/org_del.html'
     success_url = reverse_lazy('organization-list') 

# OrgMember Views
class OrgMemberList(ListView):
     model = OrgMember
     context_object_name = 'orgmember'
     template_name = 'orgmember/orgmember_list.html'
     paginate_by = 5

class OrgMemberCreateView(CreateView):
     model = OrgMember
     form_class = OrgMemberForm
     template_name = 'orgmember/orgmember_add.html'
     success_url = reverse_lazy('orgmember-list')

class OrgMemberUpdateView(UpdateView):
     model = OrgMember
     form_class = OrgMemberForm
     template_name = 'orgmember/orgmember_edit.html'
     success_url = reverse_lazy('orgmember-list')

class OrgMemberDeleteView(DeleteView):
     model = OrgMember
     template_name = 'orgmember/orgmember_del.html'
     success_url = reverse_lazy('orgmember-list')

# Student Views
class StudentList(ListView):
     model = Student
     context_object_name = 'student'
     template_name = 'student/student_list.html'
     paginate_by = 5

class StudentCreateView(CreateView):
     model = Student
     form_class = StudentForm
     template_name = 'student/student_add.html'
     success_url = reverse_lazy('student-list')

class StudentUpdateView(UpdateView):
     model = Student
     form_class = StudentForm
     template_name = 'student/student_edit.html'
     success_url = reverse_lazy('student-list')

class StudentDeleteView(DeleteView):
     model = Student
     template_name = 'student/student_del.html'
     success_url = reverse_lazy('student-list')

# College Views
class CollegeList(ListView):
     model = College
     context_object_name = 'college'
     template_name = 'college/college_list.html'
     paginate_by = 5

class CollegeCreateView(CreateView):
     model = College
     form_class = CollegeForm
     template_name = 'college/college_add.html'
     success_url = reverse_lazy('college-list')

class CollegeUpdateView(UpdateView):
     model = College
     form_class = CollegeForm
     template_name = 'college/college_edit.html'
     success_url = reverse_lazy('college-list')

class CollegeDeleteView(DeleteView):
     model = College
     template_name = 'college/college_del.html'
     success_url = reverse_lazy('college-list')

# Program Views
class ProgramList(ListView):
     model = Program
     context_object_name = 'program'
     template_name = 'program/program_list.html'
     paginate_by = 5

class ProgramCreateView(CreateView):
     model = Program
     form_class = ProgramForm
     template_name = 'program/program_add.html'
     success_url = reverse_lazy('program-list')

class ProgramUpdateView(UpdateView):
     model = Program
     form_class = ProgramForm
     template_name = 'program/program_edit.html'
     success_url = reverse_lazy('program-list')

class ProgramDeleteView(DeleteView):
     model = Program
     template_name = 'program/program_del.html'
     success_url = reverse_lazy('program-list')