## @brief Views for the instructor app.

from django.contrib.auth.decorators import login_required
from .models import Instructor, Submission, Assignment
from course.models import Course, Message, Notification, Student
from django.shortcuts import render, HttpResponse, redirect
from .forms import AssignmentForm, NotificationForm, ResourceForm
from course.forms import MessageForm
import datetime
from django.views import generic
from django.contrib.auth import get_user_model

## @brief view for the index page of the instructor.
#
# This view is called by /instructor_index url.\n
# It returns the instructor's homepage containing links to all the courses he teaches.
#us = get_user_model()

class SingleGroup(generic.DetailView):
    model = Course

    '''def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course_list"] = Student.objects.get(user=us).course_list.all()
        return context'''



class ListGroups(generic.ListView):
    model = Course

@login_required
def join_course(request, slug):
    student = Student.objects.get(user=request.user)
    #student = get_object_or_404(Group,slug=self.kwargs.get("slug"))
    student.course_list.add(Course.objects.get(slug=slug))
    print("obtained slug value",slug)
    print("obtained",student)
    return render(request, 'course/index.html')


@login_required
def instructor_index(request):
    user = request.user
    instructor = Instructor.objects.get(user=request.user)
    courses = Course.objects.filter(instructor=instructor)
    context = {
        'user': user,
        'instructor': instructor,
        'courses': courses,
    }
    return render(request, 'instructor/instructor_index.html', context)


## @brief view for the detail page of the course.
#
# This view is called by <course_id>/instructor_detail url.\n
# It returns the course's detail page containing forum and links to add assignment,resource,notifications
# and view all the assignments and their submissions.
@login_required
def instructor_detail(request, course_id):
    user = request.user
    instructor = Instructor.objects.get(user=request.user)
    courses = Course.objects.filter(instructor=instructor)
    course = Course.objects.get(id=course_id)
    messages = Message.objects.filter(course=course)
    form = MessageForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            message = form.save(commit=False)
            message.course = course
            message.sender = user
            message.time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
            message.save()
            try:
                student = Student.objects.get(user=request.user)
                return redirect('course:detail', course_id)

            except:
                return redirect('instructor:instructor_detail', course.id)

    else:
        form = MessageForm()

        context = {
                'user': user,
                'instructor': instructor,
                'course': course,
                'courses': courses,
                'messages': messages,
                'form' : form
            }

        return render(request, 'instructor/instructor_detail.html', context)


## @brief view for the course's add-notification page
#
# This view is called by <course_id>/add_notification url.\n
# It returns the webpage containing a form to add notification and redirects to the course's detail page again after the form is submitted.
@login_required
def add_notification(request, course_id):
    form = NotificationForm(request.POST or None)
    course = Course.objects.get(id=course_id)
    if form.is_valid():
        notification = form.save(commit=False)
        notification.course = course
        notification.time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y') # get the current date,time and convert into string
        notification.save()
        return redirect('instructor:instructor_detail', course.id)

    return render(request, 'instructor/add_notification.html', {'course': course, 'form': form})


## @brief view for the course's add-assignment page.
#
# This view is called by <course_id>/add_assignment url.\n
# It returns the webpage containing a form to add an assignment and redirects to the course's detail page again after the form is submitted.
@login_required
def add_assignment(request, course_id):
    form = AssignmentForm(request.POST or None, request.FILES or None)
    course = Course.objects.get(id=course_id)
    if form.is_valid():
        assignment = form.save(commit=False)
        assignment.file = request.FILES['file']
        assignment.post_time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
        assignment.course = course
        assignment.save()
        notification = Notification()
        notification.content = "New Assignment Uploaded"
        notification.course = course
        notification.time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
        notification.save()
        return redirect('instructor:instructor_detail', course.id)

    return render(request, 'instructor/create_assignment.html', {'form': form, 'course': course})


## @brief view for the course's add-resource page.
#
# This view is called by <course_id>/add_resource url.\n
# It returns the webpage containing a form to add a resource and redirects to the course's detail page again after the form is submitted.
@login_required
def add_resource(request, course_id):
    form = ResourceForm(request.POST or None, request.FILES or None)
    instructor = Instructor.objects.get(user=request.user)
    course = Course.objects.get(id=course_id)
    if form.is_valid():
        resource = form.save(commit=False)
        resource.file_resource = request.FILES['file_resource']
        resource.course = course
        resource.save()
        notification = Notification()
        notification.content = "New Resource Added - " + resource.title
        notification.course = course
        notification.time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
        notification.save()
        return redirect('instructor:instructor_detail', course.id)

    return render(request, 'instructor/add_resource.html', {'form': form, 'course': course})


## @brief view for the assignments page of a course.
#
# This view is called by <course_id>/view_all_assignments url.\n
# It returns the webpage containing all the assignments of the course and links to their submissions and feedbacks given by the students.
@login_required
def view_all_assignments(request, course_id):
    course = Course.objects.get(id=course_id)
    assignments = Assignment.objects.filter(course=course)
    return render(request, 'instructor/view_all_assignments.html', {'assignments' : assignments,'course': course})

from copyleaks.copyleakscloud import CopyleaksCloud
from copyleaks.processoptions import ProcessOptions
from copyleaks.product import Product
import sys
import time

@login_required
def plagiarism_check(request,assignment_id):
    dirPath = './copyleaks'
    if dirPath not in sys.path:
        sys.path.insert(0, dirPath)


    assignment = Assignment.objects.get(id=assignment_id)
    submissions_paths = Submission.objects.filter(assignment=assignment).values_list('file_submitted',flat=True)
    list_of_paths = []
    #for item in submissions_paths:
    #    path = r'C:\Users\home\Desktop\Courspace-master\Courspace-master\courspace\media'
    #    path = path +"\\" + item
    #    list_of_paths.append(path)
    #path = path +"\\" +'reflection.txt'


    path = r'C:\Users\home\Desktop\Courspace-master\Courspace-master\courspace\media'
    path = path +"\\" + 'submission1.txt'
    list_of_paths.append(path)
    #list_of_paths.append(path)
    #list_of_paths.append(path)

    print('custompaths ',list_of_paths)
    """
    Change to your account credentials.
    If you don't have an account yet visit https://copyleaks.com/Account/Register
    Your API-KEY is available at your dashboard on http://api.copyleaks.com of the product that you would like to use.
    Currently available products: Businesses, Education and Websites.
    """
    cloud = CopyleaksCloud(Product.Education, '<EMAIL>', 'API-KEY')

    print("You've got %s Copyleaks %s API credits" % (cloud.getCredits(), cloud.getProduct())) #get credit balance

    options = ProcessOptions()
    """
    Add this process option to your process to use sandbox mode.
    The process will not consume any credits and will return dummy results.
    For more info about optional headers visit https://api.copyleaks.com/documentation/headers
    """
    options.setSandboxMode(True)
    # Available process options
#     options.setHttpCallback("http://yoursite.here/callback")
#     options.setHttpInProgressResultsCallback("http://yoursite.here/callback/results")
#     options.setEmailCallback("Your@email.com")
#     options.setCustomFields({'Custom': 'field'})
#     options.setAllowPartialScan(True)
#     options.setCompareDocumentsForSimilarity(True)  # Available only on compareByFiles
#     options.setImportToDatabaseOnly(True)  # Available only on Education API

    print("Submitting a scan request...")
    """
    Create a scan process using one of the following methods.
    Available methods:
    createByUrl, createByOcr, createByFile, createByText and createByFiles.
    For more information visit https://api.copyleaks.com/documentation
    """
    #process = cloud.createByUrl('https://copyleaks.com', options)
    # process = cloud.createByOcr('ocr-example.jpg', eOcrLanguage.English, options)
    #process = cloud.createByFile(path, options)
    #process = cloud.createByText("Lorem ipsum torquent placerat quisque rutrum tempor lacinia aliquam habitant ligula arcu faucibus gravida, aenean orci lacinia mattis purus consectetur conubia mauris amet nibh consequat turpis dictumst hac ut nullam sodales nunc aenean pharetra, aenean ut sagittis leo massa nisi duis nullam iaculis, nulla ultrices consectetur facilisis curabitur scelerisque quisque primis elit sagittis dictum felis ornare class porta rhoncus lobortis donec praesent curabitur cubilia nec eleifend fringilla fusce vivamus elementum semper nisi conubia dolor, eros habitant nisl suspendisse venenatis interdum nulla interdum, libero urna maecenas potenti nam habitant aliquam donec class sem hendrerit tempus.")
    processes, errors = cloud.createByFiles(list_of_paths, options)

    print ("Submitted. In progress...")

    for process in processes:
        iscompleted = False
        while not iscompleted:
        # Get process status
            [iscompleted, percents] = process.isCompleted()
            print ('%s%s%s%%' % ('#' * int(percents / 2), "-" * (50 - int(percents / 2)), percents))
            if not iscompleted:
                time.sleep(2)

    print ("Process Finished!")

    result_list = []
    # Get the scan results
    for process in processes:
        results = process.getResults()
        result_list.append(results)
        print ('\nFound %s results...' % (len(results)))
        for result in results:
            print('')
            print('------------------------------------------------')
            print(result)

    context = {"result_list" : result_list}
    return render(request, 'instructor/plagiarism_report.html', context)
        # Optional: Download result full text. Uncomment to activate
        #print ("Result full-text:")
        #print("*****************")
        #print(process.getResultText(result))

        # Optional: Download comparison report. Uncomment to activate
        #print ("Comparison report:")
        #print("**************")
        #print (process.getResultComparison(result))

    # Optional: Download source full text. Uncomment to activate.
    #print ("Source full-text:")
    #print("*****************")
    #print(process.getSourceText())
    #print("Obtained submissions ",submissions.)


## @brief view for the submissions page of an assignment.
#
# This view is called by <assignment_id>/view_all_submissions url.\n
# It returns the webpage containing links to all the submissions of an assignment.
@login_required
def view_all_submissions(request,assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment)
    course = assignment.course
    return render(request, 'instructor/view_all_submissions.html', {'submissions' : submissions,'course': course,'assignment_id' : assignment_id})




## @brief view for the feedback page containing an histogram of all the feddbacks provided by the students.
#
# This view is called by <assignment_id>/view_feedback url.\n
# It returns a webpage containing the feedback received by the students organized in the form of histogram.
@login_required
def view_feedback(request,assignment_id):
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import matplotlib.ticker as ticker

    assignment = Assignment.objects.get(id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment)

    feedbacks1 = list(map(lambda x: x.feedback, submissions)) #extract the feedbacks from the submissions list
    feedbacks = np.array(feedbacks1)

    fig = plt.figure(figsize=(10,6))
    fig.suptitle('Feedback received from the students', fontsize=16, fontweight='bold')
    fig.subplots_adjust(bottom=0.3)
    ax = fig.add_subplot(111)

    ax.set_xlabel('Rating(out of 10)')
    ax.set_ylabel('Number of Students')
    x = feedbacks
    ax.hist(x, bins=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], fc='lightblue', alpha=1, align='left', edgecolor='black', linewidth=1.0)
    ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1)) #sets the difference between adjacent y-tics

    plt.figtext(0.2, 0.1, 'Average Rating : '+ str(round(np.mean(feedbacks),2)),
                bbox={'facecolor': 'lightblue', 'alpha': 0.5, 'pad': 10})     #adds box in graph to display mean rating
    plt.figtext(0.5, 0.1, 'Number of Students Students who rated : ' + str(len(feedbacks1)),
                bbox={'facecolor': 'lightblue', 'alpha': 0.5, 'pad': 10})     #adds box in graph to display number of students who rated

    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)  # converts the figure to http response
    return response
