from django.core.paginator import Paginator
from django.shortcuts import render

import json
from json.decoder import JSONDecodeError

from .forms import UploadForm
from .utils import VcfAppUtils

helper = VcfAppUtils()



def home(request):
    # Connect to the MongoDB database
    db = helper.connect_to_database()
    collection = db['variants']

    # Fetch all documents within the 'variants' collection
    variants_list = list(collection.find())

    # Set up pagination
    paginator = Paginator(variants_list, 50)  # Show 50 variants per page
    page_number = request.GET.get('page')
    variants = paginator.get_page(page_number)

    # Pass the paginated variants to the template
    return render(request, 'home.html', {'variants': variants})


def upload(request):
    # Connect to the MongoDB database
    db = helper.connect_to_database()
    collection = db['variants']

    if request.method == 'POST':        
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = request.FILES['file'].file.getvalue()
            for line in upload_file.decode('utf-8').split('\n'):
                if line.strip():
                    json_data = json.loads(line)
                    collection.insert_one(json_data)  
                    form = UploadForm()                         
    else:
        form = UploadForm()
        
    return render(request, 'upload.html', {'form': form}) 