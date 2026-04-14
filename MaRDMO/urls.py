'''URL configuration for the MaRDMO plugin.

Registers the three endpoints used by the questionnaire frontend to
communicate with background workers:

- ``mardmo/progress/<uuid>/`` — ``get_progress``: poll current task progress
- ``mardmo/show/<uuid>/``     — ``show_progress``: render live progress page
- ``mardmo/result/<uuid>/``   — ``show_success``: render completed-task result
'''

from django.urls import path
from .views import get_progress, show_progress, show_success

urlpatterns = [
    path("progress/<str:job_id>/", show_progress, name="show_progress"),
    path("progress/<str:job_id>/status/", get_progress, name="get_progress"),
    path("success/<str:job_id>/", show_success, name="show_success"),
]
