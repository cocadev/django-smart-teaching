from django.contrib.auth.models import User
from django.shortcuts import render
from registration.models import professor_profile
from .models import Marks
from .models import Enrollments, course_dashboard, student_ranks, course_exams
from django.http import HttpResponse
from django.core.paginator import Paginator
from .forms import file_class
from django.shortcuts import render
import dashboard.algo as alg
from django.contrib.auth.decorators import login_required


# import pdfkit
def add_to_database(pat, username, course_id):
    path = 'media/media_/' + pat
    co_id = course_id
    pr_id = username

    Marks.objects.filter(course_id=co_id).delete()
    Enrollments.objects.filter(course_id=co_id).delete()

    with open(path) as f:
        f1 = f.readline().split(",")
        f1[len(f1) - 1] = f1[len(f1) - 1].rstrip()

        take = return_firstline_as_tuple(f1)

        f.seek(0, 0)
        f_all = f.readlines()

        tuples = return_tuple(f_all)
        headers = [i for i in take]
        # print(list(tuples))
        # #headers = ['RollNumber', 'Name', 'exam-mid-35', 'exam-end-50', 'lab-basic01-20', 'lab-basic02-20',
        #            'lab-basic03-20', 'asgn-basic01-15', 'asgn-basic02-15', 'asgn-basic03-15', 'asgn-basic04-15',
        #            'oth-quiz01-30', 'oth-quiz02-30', 'oth-quiz03-30']
        # global df
        df = alg.initialse(tuples, headers)
        NeedyList = alg.mainFunc(df)
        CourseOverview = alg.CourseStats(df)
        ExamOverview = alg.ExamStats(df)
        Persistent_Labels = alg.PersistentLabels(df)
        Performance_Labels = alg.PerformanceLabels(df)
        student_report_details = alg.getRankMatrix(df)
        student_marks = alg.studentMarks(df)

        overall_marks = alg.OverallMarks(df)
        exam_marks = alg.ExamDetails(df)
        box_marks = alg.BoxPlot(df)
        print(box_marks)

        for i in range(len(exam_marks)):
            if len(course_exams.objects.filter(course_id=course_id, quiz_name=exam_marks[i][0])) <= 0:
                course_exams.objects.create(course_id=course_id, quiz_name=exam_marks[i][0], avg_marks=exam_marks[i][1],
                                            max_marks=exam_marks[i][2])
            else:
                p = course_exams.objects.get(course_id=course_id, quiz_name=exam_marks[i][0])
                p.quiz_name = exam_marks[i][0]
                p.avg_marks = exam_marks[i][1]
                p.max_marks = exam_marks[i][2]
                p.save()
        for i in range(len(student_report_details)):
            if len(student_ranks.objects.filter(student_id=student_report_details[i][0], course=co_id)) <= 0:
                student_ranks.objects.create(student_id=student_report_details[i][0],
                                             class_rank=student_report_details[i][1],
                                             exam_rank=student_report_details[i][2],
                                             lab_rank=student_report_details[i][3],
                                             asgn_rank=student_report_details[i][4]
                                             , oth_rank=student_report_details[i][5],
                                             course=co_id)
            else:
                p = student_ranks.objects.get(student_id=student_report_details[i][0], course=co_id)
                p.class_rank = student_report_details[i][1]
                p.exam_rank = student_report_details[i][2]
                p.lab_rank = student_report_details[i][3]
                p.asgn_rank = student_report_details[i][4]
                p.oth_rank = student_report_details[i][5]
                p.save()
        for i in range(len(student_marks)):
            p = student_marks[i][0]
            student = student_ranks.objects.get(student_id=p, course=co_id)
            student.best_marks = student_marks[i][1]
            student.worst_marks = student_marks[i][2]
            student.best_exam = student_marks[i][3]
            student.worst_exam = student_marks[i][4]
            student.save()

        # print(overall_marks)
        # print("Persistence label : ",Persistent_Labels)
        f_all[len(f_all) - 1] = f_all[len(f_all) - 1] + '\n'
        for i in range(1, len(f_all)):
            f_all[i] = f_all[i].rstrip()
            pr = student_ranks.objects.get(student_id=f_all[i][0], course=co_id)
            pr.overall = int(overall_marks[i - 1])
            # print('pr-',pr.overall)

            pr.save()
            if f_all[i] != '':
                f2 = f_all[i].split(',')
                # print(f2)
                if str(f2[0]) in Persistent_Labels[0]:
                    per_value = 'Consistent'
                elif str(f2[0]) in Persistent_Labels[1]:
                    per_value = 'Moderately Varying'
                else:
                    per_value = 'Highly Varying'

                if str(f2[0]) in Performance_Labels[0]:
                    performance_value = 'Exceptional'
                elif str(f2[0]) in Performance_Labels[1]:
                    performance_value = 'Promising'
                elif str(f2[0]) in Performance_Labels[2]:
                    performance_value = 'Average'
                else:
                    performance_value = 'Needy'

                Enrollments.objects.create(course_id=co_id, student_id=f2[0], student_name=f2[1], prof_id=pr_id,
                                           status="not_needy", persistance=per_value, performance=performance_value)
                for j in range(0, len(f2) - 2):
                    marks = f2[j + 2]
                    qname = f1[j + 2]

                    Marks.objects.create(student_name=f2[1], student_id=f2[0], marks=f2[j + 2], q_name=f1[j + 2],
                                         course_id=co_id,
                                         prof_id=pr_id)

    # all_quiz_marks_in_a_course()
    # all_quiz_marks_in_all_courses()
    return [CourseOverview, ExamOverview, NeedyList, box_marks]


#
# def call():
#     print(Marks.objects.filter(q_name="q3"))

#
# def return_tuple(line):
#     req_tuple = ()
#     for n in range(1, len(line)):
#         line[n] = line[n].rstrip()
#         x = tuple(line[n].split(','))
#         req_tuple += (x,)
#     print(req_tuple)

# tup=tuple(a)
# print(tup(0))

# a[0]=tuple(a[0])
# print(type(a[0]))

# tup=tuple(a)
#
# print(tup(0))

# @login_required()
def dashboard(request):
    form1 = file_class(request.POST, request.FILES or None)
    if request.method == 'POST':
        if form1.is_valid():
            form1.save()
            # print(request.FILES['req_file'])
            user = User.objects.get(username=request.user)
            profile = professor_profile.objects.get(professor=user)
            file1 = str(request.FILES['req_file'])
            dashboard_stats = add_to_database(file1, user.username, profile.professor_course)
            p = course_dashboard.objects.get(professor=user)
            p.course = profile.professor_course
            p.course_difficulty = dashboard_stats[0][0]
            p.course_risk = dashboard_stats[0][1]
            p.course_average = dashboard_stats[0][3]
            p.exam_difficulty = dashboard_stats[1][0]
            p.exam_cheat_risk = dashboard_stats[1][1]
            p.exam_average = dashboard_stats[1][3]
            p.quartile_1 = dashboard_stats[0][4][0]
            p.quartile_2 = dashboard_stats[0][4][1]
            p.quartile_3 = dashboard_stats[0][4][2]
            value = ''
            for j, i in enumerate(dashboard_stats[0][2]):
                if j == 0:
                    value = value + str(i)
                else:
                    value = value + '-' + str(i)
            p.course_student_list = value
            value = ''
            for j, i in enumerate(dashboard_stats[1][2]):
                if j == 0:
                    value = value + str(i)
                else:
                    value = value + '-' + str(i)
            p.exam_student_list = value
            value = ''
            for j, i in enumerate(dashboard_stats[2]):
                if j == 0:
                    value = value + str(i)
                else:
                    value = value + '-' + str(i)
            p.needy_student_list = value
            p.save()

            dashboard_marks = {'exam_marks': 0, 'lab_marks': 0, 'asgn_marks': 0, 'oth_mark': 0}
            total_marks = Marks.objects.filter(prof_id=user, course_id=profile.professor_course).all()

            marks = [i.marks for i in total_marks if i.q_name[:4] == 'exam']
            dashboard_marks['exam_marks'] = marks

            marks = [i.marks for i in total_marks if i.q_name[:3] == 'lab']
            dashboard_marks['lab_marks'] = marks

            marks = [i.marks for i in total_marks if i.q_name[:4] == 'asgn']
            dashboard_marks['asgn_marks'] = marks

            marks = [i.marks for i in total_marks if i.q_name[:3] == 'oth']
            dashboard_marks['oth_marks'] = marks

            course_risk_list = []

            for i in dashboard_stats[0][2]:
                if i != '':
                    q = Enrollments.objects.get(prof_id=user, course_id=profile.professor_course, student_id=i)
                    course_risk_list.append([q.student_name, i, q.performance, q.persistance])
            exam_risk_list = []
            for i in dashboard_stats[1][2]:
                if i != '':
                    q = Enrollments.objects.get(prof_id=user, course_id=profile.professor_course, student_id=i)
                    course_risk_list.append([q.student_name, i, q.performance, q.persistance])

            context = {'form': form1, 'courseoverview': dashboard_stats[0], 'examoverview': dashboard_stats[1],
                       'needystudents': dashboard_stats[2], 'username': user.username, 'photo': profile.professor_photo,
                       'dashboard_marks'
                       : dashboard_marks, 'course_risk_list': course_risk_list,
                       'exam_risk_list': exam_risk_list
                       }

            return render(request, "dashboard/dashboard.html", context)

        else:
            return HttpResponse("form is invalid")
    else:
        user = User.objects.get(username=request.user)
        # user = User.objects.get(username="vineet")
        profile = professor_profile.objects.get(professor=user)
        form1 = file_class()
        p = course_dashboard.objects.get(professor=user)

        coursestudents1 = p.course_student_list.split('-')

        course_risk_list = []

        for i in coursestudents1:
            if i != '':
                q = Enrollments.objects.get(prof_id=user, course_id=profile.professor_course, student_id=i)
                course_risk_list.append([q.student_name, i, q.performance, q.persistance])

        exam_risk_list = []

        course_values = (
            p.course_difficulty, p.course_risk, coursestudents1, p.course_average, [p.quartile_1, p.quartile_2,

                                                                                    p.quartile_3])

        examstudents1 = p.exam_student_list.split('-')

        for i in examstudents1:
            if i != '':
                q = Enrollments.objects.get(prof_id=user, course_id=profile.professor_course, student_id=i)
                exam_risk_list.append([q.student_name, i, q.performance, q.persistance])

        last_exam_details = (

            p.exam_difficulty, p.exam_cheat_risk, examstudents1, p.exam_average, [p.quartile_1, p.quartile_2,
                                                                                  p.quartile_3])

        needystudents1 = p.needy_student_list.split('-')
        dashboard_marks = {}
        total_marks = Marks.objects.filter(prof_id=user, course_id=profile.professor_course).all()

        if len(total_marks) == 0:
            marks = [0]
            dashboard_marks['exam_marks'] = marks
            dashboard_marks['lab_marks'] = marks
            dashboard_marks['asgn_marks'] = marks
            dashboard_marks['oth_marks'] = marks

            return render(request, "dashboard/dashboard.html",

                          {'form': form1, 'username': user.username, 'photo': profile.professor_photo,
                           'courseoverview': course_values, 'examoverview': last_exam_details,
                           'needystudents': needystudents1, 'dashboard_marks': dashboard_marks,
                           'course_risk_list': course_risk_list,
                           'exam_risk_list': exam_risk_list

                           }
                          )

        marks = [i.marks for i in total_marks if i.q_name[:4] == 'exam']
        dashboard_marks['exam_marks'] = marks

        marks = [i.marks for i in total_marks if i.q_name[:3] == 'lab']
        dashboard_marks['lab_marks'] = marks

        marks = [i.marks for i in total_marks if i.q_name[:4] == 'asgn']
        dashboard_marks['asgn_marks'] = marks

        marks = [i.marks for i in total_marks if i.q_name[:3] == 'oth']
        dashboard_marks['oth_marks'] = marks

    return render(request, "dashboard/dashboard.html",

                  {'form': form1, 'username': user.username, 'photo': profile.professor_photo,
                   'courseoverview': course_values, 'examoverview': last_exam_details,
                   'needystudents': needystudents1, 'dashboard_marks': dashboard_marks,
                   'course_risk_list': course_risk_list,
                   'exam_risk_list': exam_risk_list
                   }
                  )


# for student in students:
#     marks = tuple(row)
#     v = ag.initialize(marks, header)
#     CourseStat = CourseStats(marks)
#     ExamStat = ExamStats(marks)
#     Labels = PersistenLabels(v)
#


def needy_list(request):
    user = User.objects.get(username=request.user)
    profile = professor_profile.objects.get(professor=user)
    p = course_dashboard.objects.get(professor=user)
    needystudents = p.needy_student_list.split('-')
    needystudentdetails = []
    for i in needystudents:
        if i!='':
            j = Enrollments.objects.get(course_id=profile.professor_course, prof_id=user, student_id=i)
            needystudentdetails.append([j.student_name, j.student_id, j.performance, j.persistance])
    return render(request, "dashboard/needy_list.html",
                  {'username': user.username, 'photo': profile.professor_photo, 'needyList': needystudentdetails})


def list_of_students(request):
    user = User.objects.get(username=request.user)
    profile = professor_profile.objects.get(professor=user)
    allstudents = []
    j = Enrollments.objects.filter(course_id=profile.professor_course, prof_id=user)
    if len(j) == 0:
        allstudents.append([0, 'None', 'None', 'None','None'])
        return render(request, "dashboard/list_of_students.html",
                      {'username': user.username, 'photo': profile.professor_photo, 'allstudents': allstudents})

    for i in j:
        allstudents.append([i.student_id, i.student_name, i.persistance, i.performance,i.label])
    print(allstudents)

    paginator = Paginator(allstudents,10)

    page = request.GET.get('page')
    allstudents = paginator.get_page(page)
    return render(request, "dashboard/list_of_students.html",
                  {'username': user.username, 'photo': profile.professor_photo, 'allstudents': allstudents})


def graph(request):
    if request.method=='POST':
        user = User.objects.get(username=request.user)
        profile = professor_profile.objects.get(professor=user)
        quiz_name = str(request.POST['quizid'])
        all_students_marks = Marks.objects.filter(prof_id=user,course_id=profile.professor_course,q_name=quiz_name)
        student_quiz_marks = []
        for i in all_students_marks:
            student_quiz_marks.append([i.student_name,i.marks])
        return render(request, "dashboard/quizgraph.html", {'username': user.username, 'photo': profile.professor_photo,'data':student_quiz_marks,'quiz':quiz_name,'Maximum':quiz_name.split('-')[2]})
    else:
        user = User.objects.get(username=request.user)
        profile = professor_profile.objects.get(professor=user)
        quizzes = course_exams.objects.filter(course_id=profile.professor_course)
        quiz_name = []
        for i in quizzes:
            quiz_name.append(i.quiz_name)
        return render(request, "dashboard/graph.html",{'username': user.username, 'photo': profile.professor_photo,'quizzes':quiz_name})


def custom_404(request):
    return render(request, "dashboard/404.html")


def all_quiz_marks_in_a_course():
    b = Marks.objects.filter(student_id="55", course_id="ASE", prof_id="SUBU").values_list('q_name', 'marks')
    # print(b)
    print(type(b))


def all_quiz_marks_in_all_courses():
    print(Marks.objects.filter(student_id="55").values_list('course_id', 'q_name', 'marks'))


def return_firstline_as_tuple(fline):
    print(tuple(fline))
    return tuple(fline)


def return_tuple(line):
    req_tuple = []
    for n in range(1, len(line)):
        line[n] = line[n].rstrip()
        x = line[n].split(',')
        y = []
        y.append(x[0])
        y.append(x[1])
        for i in range(2, len(x)):
            y.append(int(x[i]))
        req_tuple += [y]
    return req_tuple
