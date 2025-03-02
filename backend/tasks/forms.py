from django import forms
from django.utils import timezone
from . import models


class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'min': timezone.now().date().isoformat()}
        )
    )
    
    class Meta:
        model = models.Task
        fields = (
            'title',
            'description',
            'priority',
            'status',
            'due_date',
        )

        widgets = {
            'title': forms.TextInput(
                attrs={'placeholder': 'Title', 'autofocus': True, 'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={'placeholder': 'Description', 'rows': 3, 'class': 'form-control'}
            ),
            'priority': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'status': forms.Select(
                attrs={'class': 'form-select'}
            ),
        }


class TaskFilterForm(forms.Form):
    FILTER_CHOICES = (
        ('all', 'All'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    
    PRIORITY_CHOICES = (
        ('all', 'All'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    SORT_CHOICES = (
        ('due_date', 'Due Date'),
        ('-priority', 'Priority (High to Low)'),
        ('priority', 'Priority (Low to High)'),
        ('-created_date', 'Newest First'),
        ('created_date', 'Oldest First'),
    )
    
    status_filter = forms.ChoiceField(
        choices=FILTER_CHOICES,
        required=False,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    priority_filter = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='due_date',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search tasks...', 'class': 'form-control'})
    )
