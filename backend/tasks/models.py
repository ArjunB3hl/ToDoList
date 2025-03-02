from django.db import models
from django.conf import settings
from django.utils import timezone


class Task(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    
    task_id = models.CharField(max_length=8, primary_key=True, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='medium'
    )
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    due_date = models.DateField(blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    completed_date = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['due_date', '-priority', 'created_date']
    
    def mark_completed(self):
        self.status = 'completed'
        self.completed_date = timezone.now().date()
        self.save()
    
    def __str__(self):
        return f'{self.user} - {self.title}'
