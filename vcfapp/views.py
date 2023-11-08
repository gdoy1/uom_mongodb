from django.core.paginator import Paginator
from django.shortcuts import render
from pymongo import MongoClient

import json
from json.decoder import JSONDecodeError

from .forms import UploadForm

def connect_to_database():
    # Connect to the MongoDB database
    client = MongoClient('mongodb://localhost:27017/')
    return client['mydatabase']    

def home(request):
    # Connect to the MongoDB database
    db = connect_to_database()
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
    db = connect_to_database()
    collection = db['variants']

    if request.method == 'POST':        
        form = UploadForm(request.POST, request.FILES)
        upload_file = request.FILES['file'].file.getvalue()
        for line in upload_file.decode('utf-8').split('\n'):
            if line.strip():
                try:
                    json_data = json.loads(line)
                    # check if name already exists in collection
                    # use same function/check as individual add variant
                    name = json_data['name']
                    if name:
                        collection.insert_one(json_data)
                except JSONDecodeError:
                    print(f'Error: follow line not in JSON format...\n{line}')
    else:
        form = UploadForm()

    return render(request, 'upload.html', {'form': form})
