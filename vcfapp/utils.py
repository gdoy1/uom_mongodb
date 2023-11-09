from pymongo import MongoClient

class VcfAppUtils():

    def __init__(self):
        self.MISSING_FIELDS = '''
            Required fields missing from JSON file.
            'name'
            'mappings' {
                'assembly_name',
                'seq_region_name',
                'start',
                'end'
            }
        '''

    def connect_to_database(self):
        # Connect to the MongoDB database
        client = MongoClient('mongodb://localhost:27017/')
        return client['mydatabase']

    def check_upload_file(self, json_data):
        # check if required keys are filled
        required_mapping_fields = [
            'assembly_name',
            'seq_region_name',
            'start',
            'end',
        ]
        required_fields = ['name']
        
        for field in required_mapping_fields:
            try:
                value = json_data['mappings'][0][field]
            except KeyError:
                error_msg = self.MISSING_FIELDS
                return error_msg
            if isinstance(value, str) and (value == '' or value is None):
                error_msg = f'required field: [{field}] is empty.'
                return error_msg
            elif isinstance(value, int) and (value == 0 or value is None):
                error_msg = f'required field: [{field}] is empty.'
                return error_msg
        
        for field in required_fields:
            try:
                value = json_data[field]
            except KeyError:
                error_msg = self.MISSING_FIELDS
                return error_msg
            if value == '' or value is None:
                error_msg = f'required field: [{field}] is empty.'
                return error_msg

        return True


    
    def is_var_unique(self, name):
        # Connect to the MongoDB database
        db = self.connect_to_database()
        collection = db['variants']

        results = [r for r in collection.find({"name": name})]

        if len(results) > 0:
            error_msg = f'Variant already exists...\n{results[0]}'
            return error_msg
        
        return True