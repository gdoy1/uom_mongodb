from pymongo import MongoClient
import retrying
from bson import ObjectId, regex
from django.contrib import messages


class VcfAppUtils:
    def __init__(self):
        self.MISSING_FIELDS = """
            Required fields missing from JSON file.
            'name'
            'mappings' {
                'assembly_name',
                'seq_region_name',
                'start',
                'end'
            }
        """

    @retrying.retry(wait_fixed=1000, stop_max_delay=10000)
    def connect_to_database(self):
        # Connect to the MongoDB database
        try:
            client = MongoClient("mongodb://localhost:27017")
            # Perform database operations here
            return client["mydatabase"]
        except Exception as e:
            print(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def check_upload_file(self, json_data):
        # check if required keys are filled
        required_mapping_fields = [
            "assembly_name",
            "seq_region_name",
            "start",
            "end",
        ]
        required_fields = ["name"]

        for field in required_mapping_fields:
            try:
                value = json_data["mappings"][0][field]
            except KeyError:
                error_msg = self.MISSING_FIELDS
                return error_msg
            if isinstance(value, str) and (value == "" or value is None):
                error_msg = f"required field: [{field}] is empty."
                return error_msg
            elif isinstance(value, int) and (value == 0 or value is None):
                error_msg = f"required field: [{field}] is empty."
                return error_msg

        for field in required_fields:
            try:
                value = json_data[field]
            except KeyError:
                error_msg = self.MISSING_FIELDS
                return error_msg
            if value == "" or value is None:
                error_msg = f"required field: [{field}] is empty."
                return error_msg

        return True

    def is_var_unique(self, name):
        # Connect to the MongoDB database
        db = self.connect_to_database()
        collection = db["variants"]

        results = [r for r in collection.find({"name": name})]

        if len(results) > 0:
            error_msg = f"Variant already exists...\n{results[0]}"
            return error_msg

        return True

    def check_single_variant_unique(
        self, assembly, chromosome, start, end, ancestral_allele, minor_allele
    ):
        db = self.connect_to_database()
        collection = db["variants"]

        results = collection.find_one(
            {
                "$and": [
                    {"mappings.assembly_name": assembly},
                    {"mappings.start": start},
                    {"mappings.end": end},
                    {"mappings.seq_region_name": chromosome},
                    {"ancestral_allele": ancestral_allele},
                    {"minor_allele": minor_allele},
                ]
            }
        )

        if results:
            error_msg = f"Variant already exists...\n{results}"
            return error_msg
        return True

    def querying_logic(self, request="", search_term1="", search_term2="", chromosome="", start_range="", end_range=""):
        """
        Querying logic to query the MongoDB database
        """
        # Connect to the MongoDB database
        db = self.connect_to_database()
        collection = db["variants"]
        # Initialize the query
        if search_term1 and search_term2 and (start_range and end_range and chromosome):
            regex_query = regex.Regex(search_term1, "i")  # 'i' for case-insensitive
            query1 = {
                "$or": [
                    {"source": regex_query},
                    {"mappings.location": regex_query},
                    {"mappings.assembly_name": regex_query},
                    {"name": regex_query},
                    {"MAF": regex_query},
                    {"ambiguity": regex_query},
                    {"var_class": regex_query},
                    {"synonyms": regex_query},
                    {"evidence": regex_query},
                    {"ancestral_allele": regex_query},
                    {"minor_allele": regex_query},
                    {"most_severe_consequence": regex_query},
                ]
            }
            regex_query2 = regex.Regex(search_term2, "i")  # 'i' for case-insensitive
            query2 = {
                "$or": [
                    {"source": regex_query2},
                    {"mappings.location": regex_query2},
                    {"mappings.assembly_name": regex_query2},
                    {"name": regex_query2},
                    {"MAF": regex_query2},
                    {"ambiguity": regex_query2},
                    {"var_class": regex_query2},
                    {"synonyms": regex_query2},
                    {"evidence": regex_query2},
                    {"ancestral_allele": regex_query2},
                    {"minor_allele": regex_query2},
                    {"most_severe_consequence": regex_query2},
                ]
            }
            query3 = {
                "$and": [
                    {"mappings.seq_region_name": chromosome},
                    {"mappings.start": {"$gte": int(start_range), "$lte": int(end_range)}},
                ]
            }
            filtered_variants_cursor = collection.find({"$and": [query1, query2, query3]})
        elif search_term1 and search_term2 and (start_range or end_range or chromosome):
            print("error - missing range")
            message = "ERROR - Chromosome and range not formatted correctly"
            messages.error(request, message)
            filtered_variants_cursor = collection.find()
        elif start_range and end_range and (search_term1 or search_term2):
            # Construct a regex query that searches all fields
            if search_term1:
                regex_query = regex.Regex(search_term1, "i")  # 'i' for case-insensitive
            elif search_term2:
                regex_query = regex.Regex(search_term2, "i")
            else:
                print("ERROR")
                message = "ERROR - Search Term failure"
                messages.error(request, message)
            query1 = {
                "$or": [
                    {"source": regex_query},
                    {"mappings.location": regex_query},
                    {"mappings.assembly_name": regex_query},
                    {"name": regex_query},
                    {"MAF": regex_query},
                    {"ambiguity": regex_query},
                    {"var_class": regex_query},
                    {"synonyms": regex_query},
                    {"evidence": regex_query},
                    {"ancestral_allele": regex_query},
                    {"minor_allele": regex_query},
                    {"most_severe_consequence": regex_query},
                ]
            }
            # Construct a query that filters by start range
            query2 = {
                "$and": [
                    {"mappings.seq_region_name": chromosome},
                    {"mappings.start": {"$gte": int(start_range), "$lte": int(end_range)}},
                ]
            }
            filtered_variants_cursor = collection.find({"$and": [query1, query2]})
            # filtered_variants_cursor = collection.find(query)
        elif start_range and end_range and chromosome:
            # Construct a query that filters by start range
            query = {
                "$and": [
                    {"mappings.seq_region_name": chromosome},
                    {"mappings.start": {"$gte": int(start_range), "$lte": int(end_range)}},
                ]
            }
            filtered_variants_cursor = collection.find(query)  # collection.find(query2)
        elif search_term1 or search_term2:
            # Construct a regex query that searches all fields
            if search_term1:
                regex_query = regex.Regex(str(search_term1), "i")  # 'i' for case-insensitive
            elif search_term2:
                regex_query = regex.Regex(str(search_term2), "i")
            else:
                print("ERROR")
                message = "ERROR - Search Term failure"
                messages.error(request, message)
            query = {
                "$or": [
                    {"source": regex_query},
                    {"mappings.location": regex_query},
                    {"mappings.assembly_name": regex_query},
                    {"name": regex_query},
                    {"MAF": regex_query},
                    {"ambiguity": regex_query},
                    {"var_class": regex_query},
                    {"synonyms": regex_query},
                    {"evidence": regex_query},
                    {"ancestral_allele": regex_query},
                    {"minor_allele": regex_query},
                    {"most_severe_consequence": regex_query},
                ]
            }
            # Construct a query that filters by start range
            filtered_variants_cursor = collection.find(query)
        elif chromosome or start_range or end_range:
            message = "ERROR - Requires chromosome and range to search"
            filtered_variants_cursor = collection.find()
            messages.error(request, message)
        else:
            filtered_variants_cursor = collection.find()
        return filtered_variants_cursor
