from django.shortcuts import render
from dashboard.models import Marks, Enrollments, User, student_ranks, course_dashboard, course_exams
from registration.models import professor_profile
from django.shortcuts import HttpResponse
from .forms import label_class

def student_report(request, id):
    if id == 0:
        return HttpResponse('No  reports to show')
    user = User.objects.get(username=request.user)
    profile = professor_profile.objects.get(professor=user)
    if request.method=='POST':
        form = label_class(request.POST)
        if form.is_valid():
            p=Enrollments.objects.get(course_id=profile.professor_course,student_id=id)
            p.label = form.cleaned_data.get('label')
            p.save()
            form = label_class()
    else:
        form = label_class()
    student_quizzes = Marks.objects.filter(prof_id=user, course_id=profile.professor_course, student_id=id)
    quizzes = []
    average_marks = []
    quiz_marks = []
    for i in student_quizzes:
        quiz_name = i.q_name
        marks = i.marks
        quiz_students = Marks.objects.filter(course_id=profile.professor_course, prof_id=user, q_name=quiz_name)
        sum = 0
        quiz_marks.append(int(marks))
        for j in quiz_students:
            sum = sum + int(j.marks)
        average = sum / len(quiz_students)
        average_marks.append(int(average))
        quizzes.append([quiz_name, marks, average])
    maximum = max(max(quiz_marks),max(average_marks))
    name = Enrollments.objects.get(prof_id=user, course_id=profile.professor_course, student_id=id)
    rank = student_ranks.objects.get(student_id=id, course=profile.professor_course)
    ranks = [rank.class_rank, rank.exam_rank, rank.lab_rank, rank.asgn_rank, rank.oth_rank]
    student_marks = [rank.best_exam, rank.best_marks, rank.worst_exam, rank.worst_marks, rank.overall]
    label = Enrollments.objects.get(course_id=profile.professor_course,student_id=id)
    return render(request, "student_report/student_report.html",
                  {'quizzes': quizzes, 'sid': id,'form':form ,'student': name.student_name, 'ranks': ranks, 'Marks': student_marks,'Maximum':maximum,'label':label.label})




def charts(request, id):
    user = User.objects.get(username=request.user)
    profile = professor_profile.objects.get(professor=user)
    if request.method == 'POST':
        form = label_class(request.POST)
        if form.is_valid():
            p = Enrollments.objects.get(course_id=profile.professor_course, student_id=id)
            p.label = form.cleaned_data.get('label')
            p.save()
            form = label_class()
    else:
        form = label_class()
    student_quizzes = Marks.objects.filter(prof_id=user, course_id=profile.professor_course, student_id=id)
    quizzes = []
    for i in student_quizzes:
        quiz_name = i.q_name
        marks = i.marks
        quiz_students = Marks.objects.filter(course_id=profile.professor_course, prof_id=user, q_name=quiz_name)
        sum = 0
        for j in quiz_students:
            sum = sum + int(j.marks)
        average = sum / len(quiz_students)
        quizzes.append([quiz_name, marks, average])
    name = Enrollments.objects.get(prof_id=user, course_id=profile.professor_course, student_id=id)
    label = Enrollments.objects.get(course_id=profile.professor_course, student_id=id)
    return render(request, "student_report/charts.html",
                  {'quizzes': quizzes, 'sid': id, 'student': name.student_name,'form':form,'label':label.label})


def tables(request, id):
    user = User.objects.get(username=request.user)
    profile = professor_profile.objects.get(professor=user)
    if request.method == 'POST':
        form = label_class(request.POST)
        if form.is_valid():
            p = Enrollments.objects.get(course_id=profile.professor_course, student_id=id)
            p.label = form.cleaned_data.get('label')
            p.save()
            form = label_class()
    else:
        form = label_class()
    student_courses = student_ranks.objects.filter(student_id=id)
    all_course_table = []
    for i in range(len(student_courses)):
        course = student_courses[i].course
        print(course)
        c_average = course_dashboard.objects.get(course=course).course_average
        all_course_table.append(
            [student_courses[i].course, student_courses[i].overall, c_average, student_courses[i].class_rank])
    this_course_table = []
    quizzes = course_exams.objects.filter(course_id=profile.professor_course)
    for i in range(len(quizzes)):
        print(quizzes[i].quiz_name)
        exam_marks = Marks.objects.get(student_id=id, prof_id=user, course_id=profile.professor_course,
                                       q_name=quizzes[i].quiz_name)
        this_course_table.append(
            [quizzes[i].quiz_name.split('-')[1], quizzes[i].avg_marks, quizzes[i].max_marks, exam_marks.marks])
    name = Enrollments.objects.get(prof_id=user, course_id=profile.professor_course, student_id=id)
    label = Enrollments.objects.get(course_id=profile.professor_course, student_id=id)
    return render(request, "student_report/tables.html",
                  {'sid': id, 'course_table': all_course_table, 'this_course': this_course_table,
                   'student': name.student_name,'form':form,'label':label.label,'course':profile.professor_course})
