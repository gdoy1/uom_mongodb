from django import forms
from django.core.exceptions import ValidationError
import json
from json.decoder import JSONDecodeError
from .utils import VcfAppUtils

helper = VcfAppUtils()

class UploadForm(forms.Form):
    file = forms.FileField()

    def clean(self):
        upload_file = self.cleaned_data['file'].file.getvalue()
        for line in upload_file.decode('utf-8').split('\n'):
            if line.strip():
                try:
                    json_data = json.loads(line)
                    print(json_data)
                    # check if required keys are filled
                    # check if name already exists in collection
                    upload_correct = helper.check_upload_file(json_data)
                    if upload_correct:
                        is_unique = helper.is_var_unique(json_data['name'])
                        if is_unique != True:
                            raise ValidationError(is_unique) 
                    else:
                        raise ValidationError(upload_correct)
                except JSONDecodeError:
                    raise ValidationError(f'Incorrect JSON format...\n{line}')
                

