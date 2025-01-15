from django import forms

FILE_TYPE_CHOICES = [
    ('pdf', 'PDF'),
    ('video', 'Video'),
    ('assignment', 'Assignment'),
]

class UploadFileForm(forms.Form):
    file_type = forms.ChoiceField(choices=FILE_TYPE_CHOICES)
    year = forms.CharField(max_length=10)
    semester = forms.CharField(max_length=10)
    title = forms.CharField(max_length=200)
    file = forms.FileField()
    description = forms.CharField(widget=forms.Textarea, required=False)
    class_name = forms.CharField(max_length=100)

    def clean_class_name(self):
        class_name = self.cleaned_data['class_name']
        # Format class_name to uppercase with a single space between words
        formatted_class_name = ' '.join(class_name.upper().split())
        return formatted_class_name

class UploadAssignmentForm(forms.Form):
    assignment = forms.FileField(required=True)