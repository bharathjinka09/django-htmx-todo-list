import json
from typing import Any, Dict, List, cast

from django.forms.models import BaseModelForm
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, DetailView, ListView
from django.urls import reverse
from django_filters.views import FilterView
from tasker.tasks.filters import TaskListFilter
from tasker.tasks.forms import TaskListCreateForm, TaskCreateForm, TaskEditForm
from tasker.tasks.models import TaskList, Task


def tasklist_list_view(request):
    context = {}
    context["object_list"] = TaskList.objects.all()
    context["form"] = TaskListCreateForm()
    context["filterset"] = TaskListFilter

    return render(request, "tasks/tasklist_list.html", context)


class TaskListFilterView(FilterView):
    filterset_class = TaskListFilter


def tasklist_create_view(request):
    context = {}
    form = TaskListCreateForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            task_list = form.save()
            response = HttpResponse()
            response["HX-Trigger"] = json.dumps({"redirect": {"url": task_list.get_absolute_url()}})
            return response

    context["form"] = form
    return render(request, "tasks/tasklist_create_form.html", context)


def tasklist_detail_view(request, slug):
    context = {}
    context["tasklist"] = TaskList.objects.get(slug=slug)

    return render(request, "tasks/tasklist_detail.html", context)


def tasklist_add_task_view(request, slug):
    context = {}
    tasklist = TaskList.objects.get(slug=slug)

    if request.method == "POST":
        cast(TaskList, tasklist.tasks.create())

    context["tasklist"] = tasklist
    return render(request, "tasks/tasklist_tasks.html", context)


def task_create_view(request, id):
    context = {}
    task_list = get_object_or_404(TaskList, id=id)

    form = TaskCreateForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.instance.task_list = task_list
            form.save()
            return HttpResponseRedirect(reverse("task-detail", kwargs={"id": form.instance.id}))

    context["form"] = form
    context["task_list_id"] = id
    return render(request, "tasks/task_create_form.html", context)


def task_edit_view(request, id):
    context = {}
    obj = get_object_or_404(Task, id=id)
    form = TaskEditForm(request.POST or None, instance=obj)

    # save the data from the form and redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse("task-detail", kwargs={"id": obj.id}))

    context["form"] = form
    return render(request, "tasks/task_edit_form.html", context)


def task_detail_view(request, id):
    context = {}
    obj = get_object_or_404(Task, id=id)
    context["task"] = obj

    return render(request, "tasks/task_detail.html", context)


def task_delete_view(request, id):
    context = {}
    obj = get_object_or_404(Task, id=id)

    if request.method == "POST":
        obj.delete()
        return render(request, "tasks/task_delete.html", context)

    return HttpResponseNotAllowed(
        [
            "POST",
        ]
    )
