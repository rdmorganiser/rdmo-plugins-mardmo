'''Django views for the MaRDMO plugin.

Provides the three AJAX endpoints used by the questionnaire frontend to
communicate with background workers, plus the ``render_preview`` helper
used by export providers to build HTML previews.

Provides:

- ``get_progress``   — JSON endpoint that returns current task progress for polling
- ``show_progress``  — HTML view that renders a live progress page for a running task
- ``show_success``   — HTML view that renders the completed-task result page
- ``render_preview`` — helper that renders a Jinja2 template with questionnaire answers
'''

from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .getters import get_item_url
from .oauth2 import _progress_store
from .store import clear_progress, _unregister_job_for_session, _job_belongs_to_session

@login_required
def get_progress(request, job_id):
    """Return the current progress data for *job_id* as a JSON response.

    Args:
        request: Django HTTP request; the user must own the job (checked via
                 the session).  Raises :exc:`~django.http.Http404` otherwise.
        job_id:  Unique job identifier string.

    Returns:
        :class:`~django.http.JsonResponse` with keys ``progress`` (int 0–100)
        and ``done`` (bool), defaulting to ``{"progress": 0, "done": False}``
        when no data is found.
    """
    if not _job_belongs_to_session(request, job_id):
        raise Http404()

    data = _progress_store.get(job_id, {"progress": 0, "done": False})
    return JsonResponse(data)


@login_required
@require_GET
def show_progress(request, job_id):
    """Render the progress-bar page for the given job.

    Args:
        request: Django HTTP request; the user must own the job (checked via
                 the session).  Raises :exc:`~django.http.Http404` otherwise.
        job_id:  Unique job identifier string passed to the template.

    Returns:
        Rendered ``MaRDMO/progress.html`` response with context ``{"job_id": job_id}``.
    """
    if not _job_belongs_to_session(request, job_id):
        raise Http404()

    return render(request, "MaRDMO/progress.html", {"job_id": job_id})


@login_required
@require_GET
def show_success(request, job_id):
    """Render the export-success page and clean up the job's progress entry.

    Args:
        request: Django HTTP request; the user must own the job (checked via
                 the session).  Raises :exc:`~django.http.Http404` otherwise.
        job_id:  Unique job identifier string; the associated progress data is
                 cleared from the cache after being read.

    Returns:
        Rendered ``MaRDMO/portalExport.html`` with the exported item IDs,
        or an error page if the job data is missing.
    """
    if not _job_belongs_to_session(request, job_id):
        raise Http404()

    job_data = _progress_store.get(job_id)
    if not job_data or "ids" not in job_data:
        return render(
            request,
            "core/error.html",
            {
                "title": "Not ready",
                "errors": ["Job not found."],
            },
        )

    # Once the success page is shown we can drop the progress entry
    clear_progress(job_id)
    _unregister_job_for_session(request, job_id)

    # Group ids by class in a fixed display order
    _CLASS_ORDER = [
        'Mathematical Model', 'Research Problem', 'Formula', 'Computational Task',
        'Quantity', 'Algorithm', 'Algorithmic Task', 'Software', 'Benchmark',
        'Workflow', 'Process Step', 'Hardware', 'CPU Model', 'Dataset',
        'Experimental Method', 'Experimental Equipment', 'Academic Discipline',
        'Programming Language', 'Publication', 'Author', 'Journal',
    ]
    grouped = defaultdict(list)
    for cls, name, qid in job_data["ids"]:
        grouped[cls].append({'name': name, 'qid': qid})
    # Split statements: those on newly created items vs. those on existing items
    created_qids = {qid for cls, name, qid in job_data["ids"]}

    stmt_map = defaultdict(list)
    relation_stmts = []
    for subj, subj_qid, prop, obj, obj_qid in job_data.get("statements", []):
        if subj_qid in created_qids:
            stmt_map[subj_qid].append({'prop': prop, 'obj': obj, 'obj_qid': obj_qid})
        else:
            relation_stmts.append({
                'subject': subj, 'subject_qid': subj_qid,
                'prop': prop, 'obj': obj, 'obj_qid': obj_qid,
            })

    # Attach statements to each item and group by class
    items_by_class = defaultdict(list)
    for cls, name, qid in job_data["ids"]:
        items_by_class[cls].append({'name': name, 'qid': qid, 'stmts': stmt_map.get(qid, [])})

    grouped_ids = [
        (cls, items_by_class[cls]) for cls in _CLASS_ORDER if cls in items_by_class
    ] + [
        (cls, items) for cls, items in items_by_class.items() if cls not in _CLASS_ORDER
    ]

    return render(
        request,
        "MaRDMO/portalExport.html",
        {
            "grouped_ids": grouped_ids,
            "relation_stmts": relation_stmts,
            "mardi_uri": get_item_url('mardi'),
        },
    )

def render_preview(self, template, answers, option, submit_label):
    """Render the documentation preview page.

    Args:
        self:     Export provider instance with ``request``, ``ExportForm``,
                  and ``project`` attributes.
        template: Template name (relative path) to include in the preview.
        answers:  Prepared answers dict passed to the template context.
        option:   Option string controlling template behaviour (passed to context).

    Returns:
        HTTP 200 response rendering ``MaRDMO/mardmoPreview.html``.
    """
    return render(
        self.request,
        'MaRDMO/mardmoPreview.html', 
        {
            'form': self.ExportForm(),
            'include_file': template,
            'include_params': {
                'title': self.project.title
            },
            'answers': answers,
            'option': option,
            'submit_label': submit_label,
            'mardiURI': get_item_url('mardi'),
            'wikidataURI': get_item_url('wikidata'),
        },
        status=200
    )
