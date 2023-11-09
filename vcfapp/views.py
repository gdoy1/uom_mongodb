from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from pymongo import MongoClient
from .forms import SingleVariantForm

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


def add_individual_data_view(request):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['mydatabase']
    collection = db['variants']

    context = {}
    context['form'] = SingleVariantForm()
    if request.POST:
        form = SingleVariantForm(request.POST)
        if form.is_valid():
            location = (
                f"{form.cleaned_data['chromosome']}:"
                f"{form.cleaned_data['start']}-"
                f"{form.cleaned_data['end']}"
            )
            ancestral_allele = form.cleaned_data['ancestral_allele']
            minor_allele = form.cleaned_data['minor_allele']
            if ancestral_allele or minor_allele:
                allele_string = (
                    f"{form.cleaned_data['ancestral_allele']}/"
                    f"{form.cleaned_data['minor_allele']}"
                )
            else:
                allele_string = None

            json_to_insert = {
                "source": "Manual single variant upload",
                "name": form.cleaned_data['name'],
                "var_class": form.cleaned_data['var_class'],
                "MAF": form.cleaned_data['maf'],
                "ambiguity": form.cleaned_data['ambiguity'],
                "mappings": [{
                    "assembly_name": form.cleaned_data['assembly'],
                    "seq_region_name": form.cleaned_data['chromosome'],
                    "strand": form.cleaned_data['strand'],
                    "coord_system": "chromosome",
                    "allele_string": allele_string,
                    "start": form.cleaned_data['start'],
                    "end": form.cleaned_data['end'],
                    "location": location,
                }],
                "ancestral_allele": form.cleaned_data['ancestral_allele'],
                "minor_allele": form.cleaned_data['minor_allele'],
                "synonyms": form.cleaned_data['synonyms'],
                "most_severe_consequence": form.cleaned_data['most_severe_consequence'],
                "evidence": form.cleaned_data['evidence']
            }

            print(json_to_insert)

            collection.insert_one(
                json_to_insert
            )
            form = SingleVariantForm()
            return HttpResponseRedirect(reverse('add-individual-var'))
    else:
        form = SingleVariantForm()

    return render(request, "single_variant.html", context)
