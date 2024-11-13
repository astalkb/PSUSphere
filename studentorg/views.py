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

from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from datetime import datetime 

@method_decorator(login_required, name='dispatch')
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
     
class ChartView(ListView):
     template_name = 'chart.html'
     def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs) 
          return context
     def get_queryset(self, *args, **kwargs):
          pass

def PieCountbySeverity(request):
     query = '''
     SELECT severity_level, COUNT(*) as count
     FROM fire_incident
     GROUP BY severity_level
     '''
     data = {}
     with connection.cursor() as cursor:
          cursor.execute(query)
          rows = cursor.fetchall()

     if rows:
          # Construct the dictionary with severity level as keys and count as values
          data = {severity: count for severity, count in rows}
     else:
          data = {}

     return JsonResponse(data)

def LineCountbyMonth(request):
     current_year = datetime.now().year
     result = {month: 0 for month in range(1, 13)}
     incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
          .values_list('date_time', flat=True)

     # Counting the number of incidents per month
     for date_time in incidents_per_month:
          month = date_time.month
          result[month] += 1

     # If you want to convert month numbers to month names, you can use a dictionary mapping
     month_names = {
          1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
          7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
     }

     result_with_month_names = {
          month_names[int(month)]: count for month, count in result.items()}
     
     return JsonResponse(result_with_month_names)

class OrganizationList(ListView):
     model = Organization
     context_object_name = 'organization'
     template_name = 'organization/org_list.html'
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

     def get_queryset(self, *args, **kwargs):
          qs = super().get_queryset(*args, **kwargs)
          if self.request.GET.get("q") != None:
               query = self.request.GET.get('q')
               qs = qs.filter(
                    Q(student__firstname__icontains=query) |
                    Q(student__lastname__icontains=query) |
                    Q(organization__name__icontains=query)
               )
          return qs

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

     def get_queryset(self):
          queryset = Student.objects.all()
          query = self.request.GET.get('q')
          if query:
               queryset = queryset.filter(
                    Q(firstname__icontains=query) |
                    Q(lastname__icontains=query) |
                    Q(middlename__icontains=query) |
                    Q(student_id__icontains=query)
               )
          return queryset

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

     def get_queryset(self, *args, **kwargs):
          qs = super().get_queryset(*args, **kwargs)
          if self.request.GET.get("q") != None:
               query = self.request.GET.get('q')
               qs = qs.filter(Q(college_name__icontains=query))
          return qs

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

     def get_queryset(self, *args, **kwargs):
          qs = super().get_queryset(*args, **kwargs)
          if self.request.GET.get("q") != None:
               query = self.request.GET.get('q')
               qs = qs.filter(Q(prog_name__icontains=query))
          return qs

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