from django import forms

from .models import ContactRequest, Project


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        if not data:
            return []
        files = data if isinstance(data, (list, tuple)) else [data]
        clean_image = super().clean
        return [clean_image(file, initial) for file in files]


class ProjectAdminForm(forms.ModelForm):
    gallery_uploads = MultipleImageField(
        required=False,
        label='Add gallery photos',
        help_text='Select several images at once. They will appear below the main photo. '
                  'Edit captions, order or remove photos in Project gallery images below.',
    )

    class Meta:
        model = Project
        fields = '__all__'


class ContactRequestForm(forms.ModelForm):
    consent = forms.BooleanField(required=True)
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'tabindex': '-1'}),
    )

    class Meta:
        model = ContactRequest
        fields = ('name', 'email', 'phone', 'interest', 'message', 'consent')
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'phone': forms.TextInput(attrs={'type': 'tel', 'autocomplete': 'tel'}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('website'):
            raise forms.ValidationError('We could not submit this request. Please try again.')
        return cleaned
