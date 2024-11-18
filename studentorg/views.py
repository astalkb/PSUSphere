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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query))
        return qs
     
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
        data = {severity: count for severity, count in rows}
    else:
        data = {}

    return JsonResponse(data)

def LineCountbyMonth(request):
    current_year = datetime.now().year
    result = {month: 0 for month in range(1, 13)}
    incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
        .values_list('date_time', flat=True)

    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    result_with_month_names = {
        month_names[int(month)]: count for month, count in result.items()}
    
    return JsonResponse(result_with_month_names)

def MultilineIncidentTop3Country(request):
    query = '''
        SELECT  
            fl.country, 
            strftime('%m', fi.date_time) AS month, 
            COUNT(fi.id) AS incident_count
        FROM  
            fire_incident fi 
        JOIN  
            fire_locations fl ON fi.location_id = fl.id 
        WHERE  
            fl.country IN ( 
                SELECT  
                    fl_top.country 
                FROM  
                    fire_incident fi_top 
                JOIN  
                    fire_locations fl_top ON fi_top.location_id = fl_top.id 
                WHERE  
                    strftime('%Y', fi_top.date_time) = strftime('%Y', 'now') 
                GROUP BY  
                    fl_top.country 
                ORDER BY  
                    COUNT(fi_top.id) DESC 
                LIMIT 3 
            ) 
            AND strftime('%Y', fi.date_time) = strftime('%Y', 'now') 
        GROUP BY  
            fl.country, month 
        ORDER BY  
            fl.country, month;
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))

    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        if country not in result:
            result[country] = {month: 0 for month in months}

        result[country][month] = total_incidents

    while len(result) < 3:
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}

    for country in result:
        result[country] = dict(sorted(result[country].items()))

    return JsonResponse(result)

def multipleBarbySeverity(request):
    query = '''
    SELECT
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM
        fire_incident fi
    GROUP BY fi.severity_level, month
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))

    for row in rows:
        level = str(row[0])
        month = row[1]
        total_incidents = row[2]

        if level not in result:
            result[level] = {month: 0 for month in months}

        result[level][month] = total_incidents

    for level in result:
        result[level] = dict(sorted(result[level].items()))

    return JsonResponse(result)

def RadarChartOrgParticipation(request):
    query = '''
    SELECT c.college_name, COUNT(DISTINCT o.id) as org_count
    FROM studentorg_college c
    LEFT JOIN studentorg_organization o ON c.id = o.college_id
    GROUP BY c.college_name
    ORDER BY org_count DESC
    LIMIT 7
    '''
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    while len(rows) < 7:
        rows.append(('Placeholder', 0))

    data = {
        'labels': [row[0] for row in rows],
        'values': [row[1] for row in rows]
    }
    
    return JsonResponse(data)

def BubbleChartStudentPrograms(request):
    query = '''
    SELECT p.prog_name, 
           COUNT(s.id) as student_count, 
           COUNT(DISTINCT o.id) as org_membership_count
    FROM studentorg_program p
    LEFT JOIN studentorg_student s ON p.id = s.program_id
    LEFT JOIN studentorg_orgmember o ON s.id = o.student_id
    GROUP BY p.prog_name
    ORDER BY student_count DESC
    LIMIT 10
    '''
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    data = {
        'labels': [row[0] for row in rows],
        'student_counts': [row[1] for row in rows],
        'org_memberships': [row[2] for row in rows]
    }
    
    return JsonResponse(data)

def HorizontalBarTopOrganizations(request):
    query = '''
    SELECT o.name, COUNT(om.id) as member_count
    FROM studentorg_organization o
    LEFT JOIN studentorg_orgmember om ON o.id = om.organization_id
    GROUP BY o.name
    ORDER BY member_count DESC
    LIMIT 5
    '''
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    data = {
        'labels': [row[0] for row in rows],
        'member_counts': [row[1] for row in rows]
    }
    
    return JsonResponse(data)

def StackedBarOrgMemberTrends(request):
    query = '''
    SELECT 
        CASE 
            WHEN strftime('%m', date_joined) IN ('01', '02', '03', '04', '05', '06') THEN 'Spring'
            WHEN strftime('%m', date_joined) IN ('07', '08', '09', '10', '11', '12') THEN 'Fall'
        END as semester,
        strftime('%Y', date_joined) as year,
        COUNT(id) as member_count
    FROM studentorg_orgmember
    GROUP BY semester, year
    ORDER BY year, semester
    '''
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    data = {
        'labels': [f"{row[1]} {row[0]}" for row in rows],
        'member_counts': [row[2] for row in rows]
    }
    
    return JsonResponse(data)

def DoughnutProgramDistribution(request):
    query = '''
    SELECT c.college_name, COUNT(p.id) as program_count
    FROM studentorg_college c
    LEFT JOIN studentorg_program p ON c.id = p.college_id
    GROUP BY c.college_name
    ORDER BY program_count DESC
    '''
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    data = {
        'labels': [row[0] for row in rows],
        'program_counts': [row[1] for row in rows]
    }
    
    return JsonResponse(data)

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