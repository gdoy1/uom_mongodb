from django.core.paginator import Paginator
from django.shortcuts import render
from pymongo import MongoClient
import pandas as pd
import retrying


@retrying.retry(wait_fixed=1000, stop_max_delay=10000)
def connect_to_mongodb():
        try:
            client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=60000)
            # Perform database operations here
            return client
        except Exception as e:
            print(f"Failed to connect to MongoDB: {str(e)}")
            raise

def home(request):
    # Connect to MongoDB
    client = connect_to_mongodb()
    #client = MongoClient('mongodb://localhost:27017/')
    db = client['mydatabase']
    collection = db['variants']

    # Fetch all documents within the 'variants' collection
    variants_list = list(collection.find())

    # Set up pagination
    paginator = Paginator(variants_list, 5000)  # Show 50 variants per page
    page_number = request.GET.get('page')
    variants = paginator.get_page(page_number)

    # Pass the paginated variants to the template
    context = {'variants': variants}
    return render(request, 'home.html', context)
