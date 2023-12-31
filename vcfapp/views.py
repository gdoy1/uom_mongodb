from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from bson import ObjectId, regex
from django.shortcuts import render
import json
from .forms import SingleVariantForm, UploadForm
from .utils import VcfAppUtils


helper = VcfAppUtils()


def home(request):
    # Get the search term and range from the GET request
    search_term1 = request.GET.get("search1", "")
    search_term2 = request.GET.get("search2", "")
    chromosome = request.GET.get("chromosome", "")
    start_range = request.GET.get("start_range", "")
    end_range = request.GET.get("end_range", "")

    filtered_variants_cursor = helper.querying_logic(
        request, search_term1, search_term2, chromosome, start_range, end_range
    )
    # Apply the query and get the count for pagination
    total_items = filtered_variants_cursor.count()

    # Pagination settings
    items_per_page = 50
    page_number = int(request.GET.get("page", 1))
    total_pages = (total_items + items_per_page - 1) // items_per_page
    skip_items = (page_number - 1) * items_per_page

    # Fetch the data for the current page with applied filtering
    variants_cursor = filtered_variants_cursor.skip(skip_items).limit(items_per_page)
    variants_list = list(variants_cursor)

    # Convert MongoDB documents to dictionaries and rename '_id' to 'id'
    variants_list = [{**doc, "id": str(doc["_id"])} for doc in variants_list]

    # Calculate pagination range
    page_range = range(1, total_pages + 1)

    # Pass the data to the template context
    context = {
        "variants": variants_list,
        "page_range": page_range,
        "current_page": page_number,
        "total_pages": total_pages,
        "total_items": total_items,
    }

    return render(request, "home.html", context)


def delete_variant(request, id):
    if request.method == "POST":
        # Connect to the MongoDB database
        db = helper.connect_to_database()
        collection = db["variants"]
        collection.delete_one({"_id": ObjectId(id)})
        return HttpResponseRedirect(reverse("home"))
    else:
        return HttpResponseRedirect(reverse("home"))


def modify_variant(request, id):
    # Connect to the MongoDB database
    db = helper.connect_to_database()
    collection = db["variants"]
    variant = collection.find_one({"_id": ObjectId(id)})
    if variant is None:
        raise Http404("Variant not found")

    if request.method == "POST":
        # Extract data from the form
        source = request.POST.get("source")
        location = request.POST.get("location")
        assembly_name = request.POST.get("assembly_name")
        end = request.POST.get("end")
        seq_region_name = request.POST.get("seq_region_name")
        strand = request.POST.get("strand")
        allele_string = request.POST.get("allele_string")
        start = request.POST.get("start")
        name = request.POST.get("name")
        maf = request.POST.get("maf")
        ambiguity = request.POST.get("ambiguity")
        var_class = request.POST.get("var_class")
        synonyms = request.POST.get("synonyms")
        evidence = request.POST.get("evidence")
        ancestral_allele = request.POST.get("ancestral_allele")
        minor_allele = request.POST.get("minor_allele")
        most_severe_consequence = request.POST.get("most_severe_consequence")

        # Create an update object
        update = {
            "source": source,
            "mappings": [
                {
                    "location": location,
                    "assembly_name": assembly_name,
                    "end": int(end),
                    "seq_region_name": seq_region_name,
                    "strand": int(strand),
                    "allele_string": allele_string,
                    "start": int(start),
                }
            ],
            "name": name,
            "MAF": maf,
            "ambiguity": ambiguity,
            "var_class": var_class,
            "synonyms": synonyms.split(
                ", "
            ),  # Assuming synonyms are a comma-separated list
            "evidence": evidence.split(
                ", "
            ),  # Assuming evidence are a comma-separated list
            "ancestral_allele": ancestral_allele,
            "minor_allele": minor_allele,
            "most_severe_consequence": most_severe_consequence,
        }

        # Update the variant in the database
        collection.update_one({"_id": ObjectId(id)}, {"$set": update})

        # Redirect back to the home page, or to a success page
        return HttpResponseRedirect(reverse("home"))
    else:
        # Include 'id' in case you need it for the form action URL
        variant["id"] = str(variant["_id"])
        # Pass the variant dictionary directly to the template.
        # It will contain all the values needed for the form fields.
        return render(request, "modify_variant.html", {"variant": variant})


def visual_summary(request):
    # Connect to the MongoDB database
    db = helper.connect_to_database()
    collection = db["variants"]

    # Aggregate the counts for each type of most_severe_consequence
    pipeline = [
        {
            "$match": {"most_severe_consequence": {"$ne": None}}
        },  # Exclude documents where most_severe_consequence is None
        {"$group": {"_id": "$most_severe_consequence", "count": {"$sum": 1}}},
    ]
    consequences = list(collection.aggregate(pipeline))

    # Exclude entries where '_id' is None
    consequences = [c for c in consequences if c["_id"] is not None]

    # Convert the aggregation result into a format suitable for the charting library
    labels = [consequence["_id"] for consequence in consequences]
    counts = [consequence["count"] for consequence in consequences]

    context = {
        "labels": labels,
        "counts": counts,
    }

    return render(request, "visual_summary.html", context)


def add_individual_data_view(request):
    # Connect to the MongoDB database
    db = helper.connect_to_database()
    collection = db["variants"]

    form = SingleVariantForm()
    if request.POST:
        form = SingleVariantForm(request.POST)
        if form.is_valid():
            location = (
                f"{form.cleaned_data['chromosome']}:"
                f"{form.cleaned_data['start']}-"
                f"{form.cleaned_data['end']}"
            )
            ancestral_allele = form.cleaned_data["ancestral_allele"].upper()
            minor_allele = form.cleaned_data["minor_allele"].upper()
            allele_string = f"{ancestral_allele}/{minor_allele}"

            json_to_insert = {
                "source": "Manual single variant upload",
                "name": form.cleaned_data["name"],
                "var_class": form.cleaned_data["var_class"],
                "MAF": form.cleaned_data["maf"],
                "ambiguity": form.cleaned_data["ambiguity"],
                "mappings": [
                    {
                        "assembly_name": form.cleaned_data["assembly"],
                        "seq_region_name": form.cleaned_data["chromosome"],
                        "strand": form.cleaned_data["strand"],
                        "coord_system": "chromosome",
                        "allele_string": allele_string,
                        "start": form.cleaned_data["start"],
                        "end": form.cleaned_data["end"],
                        "location": location,
                    }
                ],
                "ancestral_allele": form.cleaned_data["ancestral_allele"],
                "minor_allele": form.cleaned_data["minor_allele"],
                "synonyms": form.cleaned_data["synonyms"],
                "most_severe_consequence": form.cleaned_data["most_severe_consequence"],
                "evidence": form.cleaned_data["evidence"],
            }

            inserted = collection.insert_one(json_to_insert)
            doc_id = inserted.inserted_id
            messages.success(
                request, f"Variant submitted successfully! Inserted object ID: {doc_id}"
            )
            form = SingleVariantForm()
            return HttpResponseRedirect(reverse("add-individual-var"))
    else:
        form = SingleVariantForm()

    return render(request, "single_variant.html", {"form": form})


def upload(request):
    # Connect to the MongoDB database
    db = helper.connect_to_database()
    collection = db["variants"]

    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = request.FILES["file"].file.getvalue()
            for line in upload_file.decode("utf-8").split("\n"):
                if line.strip():
                    json_data = json.loads(line)
                    collection.insert_one(json_data)
            messages.success(request, 'Upload successful')
        else:
            messages.error(request, 'Upload failed')
    else:
        form = UploadForm()

    return render(request, 'upload.html', {'form': form})

def visual_summary_query(request, search1, search2, chr, start_range, end_range):
    # Connect to the MongoDB database
    db = helper.connect_to_database()
    collection = db['variants']

    if search1 == 'None': search1 = ''
    if search2 == 'None': search2 = ''
    if chr == 'None': chr = ''
    if start_range == 'None': start_range = ''
    if end_range == 'None': end_range = ''

    # call search query function
    results = helper.querying_logic(
        search_term1=search1,
        search_term2=search2,
        chromosome=chr,
        start_range=start_range,
        end_range=end_range
    )

    # Create a dictionary of consequence and their frequencies
    consequence_counts = {}
    for result in results:
        consequence = result['most_severe_consequence']
        if consequence not in consequence_counts:
            consequence_counts[consequence] = 1
        elif consequence in consequence_counts:
            consequence_counts[consequence] += 1

    # Create data lists for pie chart
    labels = []
    counts = []
    for label, count in consequence_counts.items():
        labels.append(label)
        counts.append(count)

    context = {
        'labels': labels,
        'counts': counts,
    }

    return render(request, 'visual_summary_query.html', context)
