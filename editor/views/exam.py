from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError
from django.views.generic import CreateView, UpdateView
from editor.models import Exam
from editor.views.generic import SaveContent
import os
import subprocess
import uuid

def preview(request):
    if request.is_ajax():
        try:
            fh = open(settings.GLOBAL_SETTINGS['TEMP_EXAM_FILE'], 'w')
            fh.write(request.POST['content'])
            fh.close()
        except IOError:
            message = 'Could not save exam to temporary file.'
            return HttpResponseServerError(message)
        else:
            status = subprocess.Popen(['/home/najy2/numbas/bin/numbas.py', '-p/home/najy2/numbas', '-c', '-o/srv/www/countach.ncl.ac.uk80/numbas-previews/exam', settings.GLOBAL_SETTINGS['TEMP_EXAM_FILE']], stdout = subprocess.PIPE)
            output = status.communicate()[0]
            message = 'Exam preview loaded in new window.'
        return HttpResponse(message + "\n" + output)
    

class ExamCreateView(CreateView, SaveContent):
    model = Exam
    template_name = 'exam/new.html'
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.filename = str(uuid.uuid4())
        return self.write_content(form, settings.GLOBAL_SETTINGS['EXAM_SUBDIR'])
    
    def get_success_url(self):
        return reverse('exam_edit', args=(self.object.slug,))


class ExamUpdateView(UpdateView, SaveContent):
    model = Exam
    template_name = 'exam/edit.html'
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        return self.write_content(form, settings.GLOBAL_SETTINGS['EXAM_SUBDIR'])
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            examfile = open(os.path.join(settings.GLOBAL_SETTINGS['REPO_PATH'], settings.GLOBAL_SETTINGS['EXAM_SUBDIR'], self.object.filename), 'r')
            print examfile
            self.object.content = examfile.read()
#            self.object.content = examfile.read()
            examfile.close()
        except IOError:
            self.object.content = "Could not read from exam file."
            
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))
        
    def get_success_url(self):
        return reverse('exam_edit', args=(self.object.slug,))