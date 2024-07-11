from django.test import TestCase as tc


def check_fields_of_post(post_1, post_2):
    tc_obj = tc()
    fields = ("id", "title", "text", "image", "group", "author")
    for field in fields:
        with tc.subTest(tc_obj, field=field):
            tc.assertEqual(
                tc_obj,
                getattr(post_1, field),
                getattr(post_2, field),
                f"Поле {field} не соответствует контексту.",
            )


def check_post(post_1, **data):
    tc_obj = tc()
    title = data.get("title")
    text = data.get("text")
    group = data.get("group")
    tc.assertEqual(
        tc_obj, post_1.title, title, "\nПоле title не соответствует ожидаемому значению"
    )
    tc.assertEqual(
        tc_obj, post_1.text, text, "\nПоле text не соответствует ожидаемому значению"
    )
    if not isinstance(group, int):
        group = group.id
    tc.assertEqual(
        tc_obj,
        post_1.group.id,
        group,
        "\nПоле group не соответствует ожидаемому значению",
    )
