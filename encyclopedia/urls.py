from django.urls import path

from . import views

app_name = "wiki"
urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search_request, name="search"),
    path("newpage", views.new_page, name="newpage"),
    path("editpage", views.edit_page, name="editpage"),
    path("randompage", views.random_page, name="randompage"),
    path("<str:name>", views.page, name="page")
]
 
