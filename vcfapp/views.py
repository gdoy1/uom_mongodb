from django.core.paginator import Paginator
from django.shortcuts import render
from pymongo import MongoClient

def home(request):
    # Connect to the MongoDB database
    client = MongoClient('mongodb://localhost:27017/')
    db = client['mydatabase']
    collection = db['variants']

    # Fetch all documents within the 'variants' collection
    variants_list = list(collection.find())

    # Set up pagination
    paginator = Paginator(variants_list, 50)  # Show 50 variants per page
    page_number = request.GET.get('page')
    variants = paginator.get_page(page_number)

    # Pass the paginated variants to the template
    return render(request, 'home.html', {'variants': variants})
