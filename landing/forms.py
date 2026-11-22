from django import forms

from .models import Project


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
