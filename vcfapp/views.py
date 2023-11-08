from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from pymongo import MongoClient
from bson import ObjectId

def home(request):
    # Connect to the MongoDB database
    client = MongoClient('mongodb://localhost:27017/')
    db = client['mydatabase']
    collection = db['variants']

    # Get the start coordinate from the GET request
    start_coord = request.GET.get('start')

    # Initialize the query
    query = {}
    if start_coord:
        # Adjust this line if start is stored differently in your database
        query['mappings.0.start'] = int(start_coord)

    # Apply the query and get the count for pagination
    filtered_variants_cursor = collection.find(query)
    total_items = filtered_variants_cursor.count()

    # Pagination settings
    items_per_page = 50
    page_number = int(request.GET.get('page', 1))
    total_pages = (total_items + items_per_page - 1) // items_per_page
    skip_items = (page_number - 1) * items_per_page

    # Fetch the data for the current page with applied filtering
    variants_cursor = filtered_variants_cursor.skip(skip_items).limit(items_per_page)
    variants_list = list(variants_cursor)

    # Convert MongoDB documents to dictionaries and rename '_id' to 'id'
    variants_list = [
        {**doc, 'id': str(doc['_id'])} for doc in variants_list
    ]

    # Calculate pagination range
    page_range = range(1, total_pages + 1)

    # Pass the data to the template context
    context = {
        'variants': variants_list,
        'page_range': page_range,
        'current_page': page_number,
        'total_pages': total_pages,
        'start_coord': start_coord,  # Pass the start coordinate for use in the template
    }

    return render(request, 'home.html', context)

def delete_variant(request, id):
    if request.method == "POST":
        client = MongoClient('mongodb://localhost:27017/')
        db = client['mydatabase']
        collection = db['variants']
        collection.delete_one({'_id': ObjectId(id)})
        return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseRedirect(reverse('home'))