from django.http import JsonResponse


def list_candidates(request):
    return JsonResponse(
        {
            "candidates": [{"id": 1, "name": "dummy"}],
        }
    )
