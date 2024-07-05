from django.shortcuts import render, redirect # type: ignore
from .forms import CustomStaffProfileForm # type: ignore
from django.http import Http404, FileResponse # type: ignore
from django.conf import settings # type: ignore
import os

# Create your views here.
class StaffProfileViews():
    def general_view(request):
        return render(request, 'admin/profile_general.html')
    
    def edit_profile_view(request):
        if request.method == 'POST':
            form = CustomStaffProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('admin:staff_profile_general_view')
        else:
            form = CustomStaffProfileForm(instance=request.user)
        return render(request, 'admin/profile_edit.html', {'form':form})
    
    def error_404(request):
        raise Http404
    
    # def change_password_view(request):
    #     return render(request, 'admin/profile_change_password.html')

class MediaFileView():
    def course_media_view(request, file_path):
        # Define the path to the specific folder within MEDIA_ROOT
        specific_folder_path = os.path.join(settings.MEDIA_ROOT, 'course_cover_images')

        # Get the full path to the requested file
        requested_file_path = os.path.join(specific_folder_path, file_path)

        # Check if the file exists within the specific folder
        if not os.path.isfile(requested_file_path):
            raise Http404

        # Serve the file
        file = open(requested_file_path, 'rb')
        response = FileResponse(file)
        return response
    
    
def error_404_view(request, exception):
    rpath = request.path.split('/')
    if request.user.is_superuser and rpath[1] == 'admin':
        return render(request, 'admin/404.html', status=404)
    else:
        return render(request, '404.html', status=404)