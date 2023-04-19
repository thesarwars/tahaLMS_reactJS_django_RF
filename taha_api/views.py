from django.shortcuts import render
from .serializers import TeacherSerializer, CategorySerializer, CourseSerializer, ChapterSerializer, StudentSerializer
from .serializers import EnrollCourseSerializer, CourseRatingSerializer, TeacherDashboardSerializer, AddToFavSerializer

from .models import *
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
# Create your views here.

class TeacherList(generics.ListCreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    # permission_classes = [permissions.IsAuthenticated]
    
    
    # def get_queryset(self):
    #     teacher_name = self.kwargs('full_name')
    #     teacher = Teacher.objects.get(pk=teacher_name)
    #     return Teacher.objects.filter(teacher=teacher)


class TeacherUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    # permission_classes = [permissions.IsAuthenticated]
    # lookup_field = ['pk']
    
    # def get_queryset(self):
    #     teacher_id = self.kwargs['teacher_id']
    #     teacher = Teacher.objects.get(pk=teacher_id)
    #     return Course.objects.filter(teacher=teacher)
        
        
class TeacherDashboardView(generics.RetrieveAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherDashboardSerializer
    

@csrf_exempt    
def teacher_login(request):
    email = request.POST['email']
    password = request.POST['password']
    try:
        teacherData = Teacher.objects.get(email=email, password=password)
    except Teacher.DoesNotExist:
        teacherData = None
    
    if teacherData:
        return JsonResponse({'bool': True, 'teacher_id': teacherData.id})
    else:
        return JsonResponse({'bool': False})

# class TeacherList(APIView):
#     def get(self, request, format=None):
#         teacher = Teacher.objects.all()
#         serializer = TeacherSerializer(teacher, many=True)
#         return Response(serializer.data)
    
#     def post(self, request, format=None):
#             serializer = TeacherSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryList(generics.ListCreateAPIView):
    queryset = CourseCategory.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [permissions.IsAuthenticated]

# Course
class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        if 'result' in self.request.GET:
            qs = Course.objects.all().order_by('-id')[:4]
            
        if 'category' in self.request.GET:
            category = self.request.GET['category']
            qs = Course.objects.filter(techs__icontains = category)
        
        if 'skill_name' in self.request.GET and 'teacher' in self.request.GET:
            skill_name = self.request.GET['skill_name']
            teacher = self.request.GET['teacher']
            teacher = Teacher.objects.filter(id=teacher).first()
            qs = Course.objects.filter(techs__icontains = skill_name, teacher=teacher)
        
        
        #  recommended course function   
        
        elif 'studentId' in self.kwargs:
            student_id = self.kwargs['studentId']
            student = Student.objects.get(pk=student_id)
            queries = [Q(techs__iendswith=value) for value in student.intereseted_cat]
            query = queries.pop()
            for item in queries:
                query |= item
            qs = Course.objects.filter(query)
            return qs
        
        #  recommended course function end
        
        return qs

# Specific course detail
class CourseListDetail(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # permission_classes = [permissions.IsAuthenticated]


class ChapterList(generics.ListCreateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    # permission_classes = [permissions.IsAuthenticated]


# Specific chapter details
class ChapterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    # permission_classes = [permissions.IsAuthenticated]


# Specific Teacher Course
class TeacherCourseList(generics.ListAPIView):
    serializer_class = CourseSerializer
    # permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = Teacher.objects.get(pk=teacher_id)
        return Course.objects.filter(teacher=teacher)



# Specific Course chapter list
class CourseChapterList(generics.ListAPIView):
    serializer_class = ChapterSerializer
    # permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = Course.objects.get(pk=course_id)
        return Chapter.objects.filter(course=course)
    

# Student section

class StudentList(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    # permission_classes = [permissions.IsAuthenticated]

@csrf_exempt    
def student_login(request):
    email = request.POST['email']
    password = request.POST['password']
    try:
        studentData = Student.objects.get(email=email, password=password)
    except Student.DoesNotExist:
        studentData = None
    
    if studentData:
        return JsonResponse({'bool': True, 'student_id': studentData.id})
    else:
        return JsonResponse({'bool': False})
    
    

# Student enroll in course
class EnrollStudentList(generics.ListCreateAPIView):
    queryset = EnrollCourseStudent.objects.all()
    serializer_class = EnrollCourseSerializer
    
    
def enroll_status(request, student_id, course_id):
    student = Student.objects.filter(id=student_id).first()
    course = Course.objects.filter(id=course_id).first()
    enrollStatus = EnrollCourseStudent.objects.filter(course=course, student=student).count()
    
    if enrollStatus:
        return JsonResponse({'bool': True})
    else:
        return JsonResponse({'bool': False})
    
    
class EnrolledStudentsView(generics.ListAPIView):
    queryset = EnrollCourseStudent.objects.all()
    serializer_class = EnrollCourseSerializer
    
    def get_queryset(self):
        if 'course_id' in self.kwargs:
            course_id = self.kwargs['course_id']
            course = Course.objects.get(pk=course_id)
            return EnrollCourseStudent.objects.filter(course=course)
        
        # fetcing student enrolled (all) in course in teacher account
        elif 'teacher_id' in self.kwargs:
            teacher_id = self.kwargs['teacher_id']
            teacher = Teacher.objects.get(pk=teacher_id)
            return EnrollCourseStudent.objects.filter(course__teacher=teacher).distinct()
        # end
        
        # fetcing student enrolled in course in student account
        elif 'student_id' in self.kwargs:
            student_id = self.kwargs['student_id']
            student = Student.objects.get(pk=student_id)
            return EnrollCourseStudent.objects.filter(student=student).distinct()
        # end
    
    
# Course rating by student
class RatingCourseView(generics.ListCreateAPIView):
    queryset = CourseRating.objects.all()
    serializer_class = CourseRatingSerializer
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = Course.objects.get(pk=course_id)
        return CourseRating.objects.filter(course=course)
    
    
def rating_status(request, student_id, course_id):
    student = Student.objects.filter(id=student_id).first()
    course = Course.objects.filter(id=course_id).first()
    enrollStatus = CourseRating.objects.filter(course=course, student=student).count()
    
    if enrollStatus:
        return JsonResponse({'bool': True})
    else:
        return JsonResponse({'bool': False})
    
# End

# Student add course to favourite list
class AddToFavView(generics.ListCreateAPIView):
    queryset = AddToFav.objects.all()
    serializer_class = AddToFavSerializer
    
    
def favourite_status(request, student_id, course_id):
    student = Student.objects.filter(id=student_id).first()
    course = Course.objects.filter(id=course_id).first()
    favouriteStatus = AddToFav.objects.filter(course=course, student=student).first()
    
    if favouriteStatus and favouriteStatus.status == True:
        return JsonResponse({'bool': True})
    else:
        return JsonResponse({'bool': False})
    
    
def del_favourite_status(request, student_id, course_id):
    student = Student.objects.filter(id=student_id).first()
    course = Course.objects.filter(id=course_id).first()
    favouriteStatus = AddToFav.objects.filter(course=course, student=student).delete()
    
    if favouriteStatus:
        return JsonResponse({'bool': True})
    else:
        return JsonResponse({'bool': False})