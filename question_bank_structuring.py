from collections import Counter


def structure_question_bank(data):
    if not data:
        raise ValueError("The JSON data is empty.")

    exam_infos = [item.get("exam_info", {}) for item in data]

    def get_most_common(values, default=None):
        if not values:
            return default
        counter = Counter(values)
        most_common_value, _ = counter.most_common(1)[0]
        return most_common_value

    consensus_exam_info = {}
    fields = ["exam_name", "exam_year", "exam_section"]

    for field in fields:
        field_values = [info.get(field) for info in exam_infos if field in info]
        consensus_value = get_most_common(field_values, default="")
        consensus_exam_info[field] = consensus_value

    questions = [
        {
            "question": item.get("question", {}),
            "solution": item.get("solution", {})
        } for item in data
    ]

    structured_json = {
        "exam_info": consensus_exam_info,
        "questions": questions
    }

    return structured_json