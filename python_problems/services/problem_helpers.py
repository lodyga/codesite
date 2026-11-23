import re
from django.db.models import Q
from python_problems.models import Problem, ProblemType


def get_problem_metadata(problem):
    # Not needed.
    # Metadata checked in viwew.py
    if problem.metadata is None:
        raise ValueError("No problem metadata.")

    metadata = problem.metadata

    if "problem_type" not in metadata:
        raise ValueError("No problem type in metadata.")
    elif "comparison_type" not in metadata:
        raise ValueError("No comparison type in metadata.")

    if metadata["problem_type"] == ProblemType.CLASS:
        if "class_name" not in metadata:
            raise ValueError("No class name in metadata.")
    else:
        if "method_name" not in metadata:
            raise ValueError("No method name in metadata.")
        elif "parameters" not in metadata:
            raise ValueError("No parameters in metadata.")
        elif "return_type" not in metadata:
            raise ValueError("No return type in metadata.")

    return metadata


def parse_url(raw_url):
    return re.search(r"((https?)://)?(www\.)?(app\.)?(\w+\.\w+)(/)?", raw_url).group(5)


def get_filtered_problem_queryset(params, language_name=None):
    queryset = (
        Problem.objects
        .select_related("difficulty", "owner")
        .prefetch_related("tags", "solutions__language")
    )

    def get_param(name):
        return params.get(name) if params is not None else None

    query_text = get_param("query_text")
    difficulty_id = get_param("difficulty_id")
    tag_id = get_param("tag_id")
    language_id = get_param("language_id")
    order_by = get_param("order_by") or "created_at"

    if difficulty_id and str(difficulty_id) != "0":
        try:
            queryset = queryset.filter(difficulty_id=int(difficulty_id))
        except (TypeError, ValueError):
            pass

    if language_id and str(language_id) != "0":
        try:
            queryset = queryset.filter(
                solutions__language_id=int(language_id)
            ).distinct()
        except (TypeError, ValueError):
            pass
    elif str(language_id) not in ("0",) and language_name:
        queryset = queryset.filter(
            solutions__language__name=language_name
        ).distinct()

    if tag_id and str(tag_id) != "0":
        try:
            queryset = queryset.filter(tags__id=int(tag_id))
        except (TypeError, ValueError):
            pass

    if query_text:
        queryset = queryset.filter(
            Q(tags__name__icontains=query_text) |
            Q(title__icontains=query_text)
        ).distinct()

    allowed_order_fields = {
        "difficulty",
        "title",
        "owner",
        "created_at",
        "updated_at",
    }
    if order_by not in allowed_order_fields:
        order_by = "created_at"

    return queryset.order_by(order_by)


def get_adjacent_slugs(problem, params=None, language_name=None):
    problem_list = get_filtered_problem_queryset(params, language_name)

    problem_ids = list(problem_list.values_list("id", flat=True))

    if problem.id not in problem_ids:
        return (None, None)

    problem_index = problem_ids.index(problem.id)

    prev_problem_id = problem_ids[problem_index - 1]

    next_problem_id = problem_ids[(problem_index + 1) % len(problem_ids)]

    prev_problem_slug = Problem.objects.filter(
        id=prev_problem_id).first().slug

    next_problem_slug = Problem.objects.filter(
        id=next_problem_id).first().slug

    return (prev_problem_slug, next_problem_slug)


def parse_problem_description(problem_description):
    if not problem_description:
        return ("", [])

    normalized = problem_description.replace("\r\n", "\n")

    def clean_segment(text):
        cleaned = re.sub(r"(?i)</?p>", "\n", text)
        cleaned = re.sub(r"(?i)<br\s*/?>", "\n", cleaned)
        cleaned = re.sub(r"(?i)</?b>", "", cleaned)
        lines = [line for line in cleaned.split("\n")]

        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()

        if lines[0].startswith("Example "):
            lines.pop(0)
        return "\n".join(lines)

    pre_blocks = re.findall(r"(?is)<pre>(.*?)</pre>", normalized)
    question_raw = normalized.split(
        "<pre>", 1)[0] if pre_blocks else normalized

    question = clean_segment(question_raw)
    examples = []
    for block in pre_blocks:
        cleaned_block = clean_segment(block)
        if cleaned_block:
            examples.append(cleaned_block)

    return (question, examples)
