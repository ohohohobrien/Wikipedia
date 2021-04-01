from django.shortcuts import redirect, render
from . import util
import markdown2
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings as django_settings
import os
import sys
from random import randint

class SearchForm(forms.Form):
    search = forms.CharField(label="Search")

class NewPageForm(forms.Form):
    title = forms.CharField(max_length=100, label="Title")
    message = forms.CharField(widget=forms.Textarea, label="")

class EditPageForm(forms.Form):

    message = forms.CharField(widget=forms.Textarea, label="", required=False)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def page(request, name):

    page = util.get_entry(name)

    # check if page exists
    if page:

        if "current_page" not in request.session:

            # If not, create a new list
            request.session["current_page"] = []

        request.session['current_page'] = name

        # render the requested page
        return render(request, "encyclopedia/page.html", {
            "page_name": name,
            "content": markdown2.markdown(page)
        })

    else:
        # return error
        return render(request, "encyclopedia/error.html", {
            "page_name": name,
            "error_header": "This page doesn't exist.",
            "error_message": f"We are sorry but the page '<i>{name}</i>' doesn't exist. But it can if you want? Why not make the page!."
        })

def edit_page(request):

    name = request.session.get('current_page')
    page = util.get_entry(name)
    content = page
    form = EditPageForm()
    form.fields['message'].initial = str(content)
    
    if request.method == "POST":
        edited_form = EditPageForm(request.POST)

        if edited_form.is_valid():
            
            new_content = edited_form.cleaned_data["message"]
            util.save_entry(name, new_content)
            page = util.get_entry(name)

            url = reverse('wiki:page', kwargs={'name': name})
            return HttpResponseRedirect(url)

    # check if page exists
    if page:
        return render(request, "encyclopedia/editpage.html", {
            "page_name": name,
            "form": form,
        })

    else:
        return render(request, "encyclopedia/error.html", {
            "page_name": name
        })

def new_page(request):

    if request.method == "POST":
        # do something with form information

        # Take in the data the user submitted and save it as form
        form = NewPageForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the title from the 'cleaned' version of form data
            title = form.cleaned_data["title"]

            # Check if title already exists
            if util.get_entry(title):
                # show warning
                messages.error(request, 'Page with title already exists')   
                return render(request, "encyclopedia/newpage.html", {
                    "form": form
                })

            else:

                article_content = form.cleaned_data["message"]
                file_name = title + ".md"
                test_name = os.path.join("entries\\", file_name)

                with open(test_name, "a") as f:
                    f.write("# " + title)
                    f.write("\n\n")
                    f.write(article_content)
                    f.close()

            # Redirect user to new page
            page_title = str(title)

            url = reverse('wiki:page', kwargs={'name': page_title})
            return HttpResponseRedirect(url)

        else:

            # If the form is invalid, re-render the page with existing information.
            return render(request, "encyclopedia/newpage.html", {
                "form": form
            })

    return render(request, "encyclopedia/newpage.html", {
        "form": NewPageForm()
    })
    

def search(search_input):

    # check if search is succesful
    search_test = str(search_input).lower()

    test = util.list_entries()
    found_test = []

    for i in range(len(test)):
        if search_test in test[i].lower():
            found_test.append(test[i])

    # check if direct match

    length = len(found_test)
    direct_match = False

    for i in range(length):
        if search_test == found_test[i].lower():
            direct_match = True

    # return the results

    if (length < 1):                  
        return (length)                                     # no matches
    elif (length == 1):               
        return (length, found_test, direct_match)           # 1 match
    else:                             
        return (length, found_test)                         # multiple matches

def search_request(request):

    if (request.method == "POST"):

        inp_value = request.POST.get('q')

        search_result = search(inp_value)

        # Redirect to correct page

        # return error
        if search_result == 0:
            return render(request, "encyclopedia/error.html", {
                "page_name": inp_value,
                "error_header": "We didn't find anything for you.",
                "error_message": f"We are sorry but there are no results for '<i>{inp_value}</i>'. Please check the spelling."
            })
        # return page searched
        elif search_result[0] == 1:
            if search_result[2] == True:            # direct match
                content_to_show = str(search_result[1])[2:-2]  
                url = reverse('wiki:page', kwargs={'name': content_to_show})
                return HttpResponseRedirect(url)
            else:                                   # not a direct match
                print(search_result[1])
                return render(request, "encyclopedia/search.html", {
                    "search_results": search_result[1],
                    "search_input": inp_value
                })
        # return multiple search results
        else:
            return render(request, "encyclopedia/search.html", {
                "search_results": search_result[1],
                "search_input": inp_value
            })

def random_page(request):
    page_list = util.list_entries()
    length = len(page_list) - 1
    random_page = randint(0, length)
    name = page_list[random_page]
    request.session['current_page'] = name
    url = reverse('wiki:page', kwargs={'name': name})
    return HttpResponseRedirect(url)