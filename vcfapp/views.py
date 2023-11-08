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

# Other imports ...

def modify_variant(request, id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['mydatabase']
    collection = db['variants']
    variant = collection.find_one({'_id': ObjectId(id)})
    if variant is None:
        raise Http404("Variant not found")

    if request.method == 'POST':
        # Extract data from the form
        source = request.POST.get('source')
        location = request.POST.get('location')
        assembly_name = request.POST.get('assembly_name')
        end = request.POST.get('end')
        seq_region_name = request.POST.get('seq_region_name')
        strand = request.POST.get('strand')
        allele_string = request.POST.get('allele_string')
        start = request.POST.get('start')
        name = request.POST.get('name')
        maf = request.POST.get('maf')
        ambiguity = request.POST.get('ambiguity')
        var_class = request.POST.get('var_class')
        synonyms = request.POST.get('synonyms')
        evidence = request.POST.get('evidence')
        ancestral_allele = request.POST.get('ancestral_allele')
        minor_allele = request.POST.get('minor_allele')
        most_severe_consequence = request.POST.get('most_severe_consequence')

        # Create an update object
        update = {
            'source': source,
            'mappings': [{
                'location': location,
                'assembly_name': assembly_name,
                'end': int(end),
                'seq_region_name': seq_region_name,
                'strand': int(strand),
                'allele_string': allele_string,
                'start': int(start)
            }],
            'name': name,
            'MAF': maf,
            'ambiguity': ambiguity,
            'var_class': var_class,
            'synonyms': synonyms.split(', '),  # Assuming synonyms are a comma-separated list
            'evidence': evidence.split(', '),  # Assuming evidence are a comma-separated list
            'ancestral_allele': ancestral_allele,
            'minor_allele': minor_allele,
            'most_severe_consequence': most_severe_consequence
        }

        # Update the variant in the database
        collection.update_one({'_id': ObjectId(id)}, {'$set': update})

        # Redirect back to the home page, or to a success page
        return HttpResponseRedirect(reverse('home'))
    else:
        # Include 'id' in case you need it for the form action URL
        variant['id'] = str(variant['_id'])
        # Pass the variant dictionary directly to the template.
        # It will contain all the values needed for the form fields.
        return render(request, 'modify_variant.html', {'variant': variant})
