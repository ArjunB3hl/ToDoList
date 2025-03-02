from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from . import models
from . import forms
from . import functions


def tasks(request):
    if request.method == 'GET':
        filter_form = forms.TaskFilterForm(request.GET or None)
        
        if request.user.is_authenticated:
            tasks_queryset = models.Task.objects.filter(user=request.user)
            
            # Apply filters if form is valid
            if filter_form.is_valid():
                status_filter = filter_form.cleaned_data.get('status_filter')
                priority_filter = filter_form.cleaned_data.get('priority_filter')
                sort_by = filter_form.cleaned_data.get('sort_by')
                search_query = filter_form.cleaned_data.get('search')
                
                # Filter by status
                if status_filter and status_filter != 'all':
                    tasks_queryset = tasks_queryset.filter(status=status_filter)
                
                # Filter by priority
                if priority_filter and priority_filter != 'all':
                    tasks_queryset = tasks_queryset.filter(priority=priority_filter)
                
                # Search in title and description
                if search_query:
                    tasks_queryset = tasks_queryset.filter(
                        Q(title__icontains=search_query) | 
                        Q(description__icontains=search_query)
                    )
                
                # Sort results
                if sort_by:
                    tasks_queryset = tasks_queryset.order_by(sort_by)
            
            tasks = tasks_queryset
            total = tasks.count()
            
            # Get overdue tasks
            today = timezone.now().date()
            overdue_count = tasks_queryset.filter(
                due_date__lt=today, 
                status__in=['pending', 'in_progress']
            ).count()
            
        else:
            # For non-authenticated users, use cookies
            tasks_list = functions.get_tasks_cookies(request)
            
            # Apply basic filtering for cookie-based tasks
            if filter_form.is_valid():
                status_filter = filter_form.cleaned_data.get('status_filter')
                priority_filter = filter_form.cleaned_data.get('priority_filter')
                search_query = filter_form.cleaned_data.get('search')
                
                filtered_tasks = tasks_list
                
                # Filter by status
                if status_filter and status_filter != 'all':
                    filtered_tasks = [t for t in filtered_tasks if t.get('status', 'pending') == status_filter]
                
                # Filter by priority
                if priority_filter and priority_filter != 'all':
                    filtered_tasks = [t for t in filtered_tasks if t.get('priority', 'medium') == priority_filter]
                
                # Search in title and description
                if search_query:
                    filtered_tasks = [
                        t for t in filtered_tasks 
                        if search_query.lower() in t.get('title', '').lower() 
                        or search_query.lower() in t.get('description', '').lower()
                    ]
                
                tasks = filtered_tasks
            else:
                tasks = tasks_list
            
            total = len(tasks)
            overdue_count = 0  # Simplified for cookie-based tasks
        
        context = {
            'tasks': tasks,
            'total': total,
            'filter_form': filter_form,
            'overdue_count': overdue_count,
        }

        return render(request, 'tasks/index.html', context)


def tasks_add(request):
    if request.method == 'GET':
        form = forms.TaskForm()

        context = {
            'form': form,
        }

        return render(request, 'tasks/add.html', context)
    elif request.method == 'POST':
        response = redirect('tasks')

        if request.user.is_authenticated:
            form = forms.TaskForm(request.POST)

            if form.is_valid():
                new_task = form.save(commit=False)
                new_task.user = request.user
                new_task.task_id = functions.generate_id()

                try:
                    new_task.save()
                    messages.success(request, 'Task created successfully!')
                except IntegrityError:
                    messages.error(request, 'Error creating task. Please try again.')
                    return HttpResponse(status=500)
            else:
                messages.error(request, 'Please correct the errors in the form.')
                return render(request, 'tasks/add.html', {'form': form})
        else:
            # For non-authenticated users
            title = request.POST.get('title')
            description = request.POST.get('description')
            priority = request.POST.get('priority', 'medium')
            status = request.POST.get('status', 'pending')
            due_date_str = request.POST.get('due_date')
            
            tasks = functions.get_tasks_cookies(request)

            new_task = {
                'task_id': functions.generate_id(),
                'title': title,
                'description': description,
                'priority': priority,
                'status': status,
                'due_date': due_date_str if due_date_str else None,
                'created_date': functions.get_datetime(),
                'completed_date': None,
            }

            tasks.append(new_task)

            response.set_cookie(
                'tasks',
                tasks,
                expires=functions.get_expire_datetime(),
            )
            
            messages.success(request, 'Task created successfully!')

        return response


def tasks_edit(request, pk):
    if request.method == 'GET':
        context = {}

        if request.user.is_authenticated:
            task = get_object_or_404(models.Task, task_id=pk, user=request.user)
            form = forms.TaskForm(instance=task)
        else:
            tasks = functions.get_tasks_cookies(request)

            task = next(
                (task for task in tasks if task.get('task_id') == pk), 
                None,
            )

            if task is None:
                return HttpResponse(status=404)

            initial = {
                'title': task.get('title'),
                'description': task.get('description'),
                'priority': task.get('priority', 'medium'),
                'status': task.get('status', 'pending'),
                'due_date': task.get('due_date'),
            }

            form = forms.TaskForm(initial=initial)

            context.update(
                {'datetime': functions.str_to_datetime(task.get('created_date'))}
            )

        context.update({'task': task, 'form': form})

        return render(request, 'tasks/edit.html', context)
    elif request.method == 'POST':
        response = redirect('tasks')

        if request.user.is_authenticated:
            task = get_object_or_404(models.Task, task_id=pk, user=request.user)
            form = forms.TaskForm(request.POST, instance=task)

            if form.is_valid():
                # Check if task is being marked as completed
                if task.status != 'completed' and form.cleaned_data['status'] == 'completed':
                    task.completed_date = timezone.now().date()
                
                form.save()
                messages.success(request, 'Task updated successfully!')
            else:
                messages.error(request, 'Please correct the errors in the form.')
                return render(request, 'tasks/edit.html', {'form': form, 'task': task})
        else:
            tasks = functions.get_tasks_cookies(request)
            edit_task = next(task for task in tasks if task.get('task_id') == pk)

            title_updated = request.POST.get('title')
            description_updated = request.POST.get('description')
            priority_updated = request.POST.get('priority', 'medium')
            status_updated = request.POST.get('status', 'pending')
            due_date_updated = request.POST.get('due_date')
            
            # Check if task is being marked as completed
            completed_date = None
            if edit_task.get('status') != 'completed' and status_updated == 'completed':
                completed_date = timezone.now().date().isoformat()

            edit_task.update({
                'title': title_updated, 
                'description': description_updated,
                'priority': priority_updated,
                'status': status_updated,
                'due_date': due_date_updated if due_date_updated else None,
                'completed_date': completed_date,
            })

            updated_tasks = [
                edit_task if task.get('task_id') == pk else task for task in tasks
            ]

            response.set_cookie(
                'tasks',
                updated_tasks,
                expires=functions.get_expire_datetime(),
            )
            
            messages.success(request, 'Task updated successfully!')

        return response


def tasks_delete(request, pk):
    if request.method == 'GET':
        response = redirect('tasks')

        if request.user.is_authenticated:
            task = get_object_or_404(models.Task, task_id=pk, user=request.user)
            task.delete()
            messages.success(request, 'Task deleted successfully!')
        else:
            tasks = functions.get_tasks_cookies(request)

            if len(tasks) == 1:
                if tasks[0].get('task_id') != pk:
                    return HttpResponse(status=404)

                response.delete_cookie('tasks')
            else:
                updated_tasks = [
                    task for task in tasks if task.get('task_id') != pk
                ]

                if updated_tasks == tasks:
                    return HttpResponse(status=404)

                response.set_cookie(
                    'tasks',
                    updated_tasks,
                    expires=functions.get_expire_datetime(),
                )
            
            messages.success(request, 'Task deleted successfully!')

        return response


def tasks_complete(request, pk):
    """Mark a task as completed without deleting it"""
    if request.method == 'GET':
        response = redirect('tasks')

        if request.user.is_authenticated:
            task = get_object_or_404(models.Task, task_id=pk, user=request.user)
            task.mark_completed()
            messages.success(request, 'Task marked as completed!')
        else:
            tasks = functions.get_tasks_cookies(request)
            task = next((t for t in tasks if t.get('task_id') == pk), None)
            
            if not task:
                return HttpResponse(status=404)
            
            task['status'] = 'completed'
            task['completed_date'] = timezone.now().date().isoformat()
            
            updated_tasks = [
                task if t.get('task_id') == pk else t for t in tasks
            ]
            
            response.set_cookie(
                'tasks',
                updated_tasks,
                expires=functions.get_expire_datetime(),
            )
            
            messages.success(request, 'Task marked as completed!')
            
        return response
