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


def check_post(post_1, post_2, **data):
    tc_obj = tc()
    tc.assertEqual(tc_obj, post_1.text, data["text"])
    tc.assertEqual(tc_obj, post_1.group_id, data["group"])
    tc.assertEqual(tc_obj, post_1.author, post_2.author)


def check_post_2(post_1, post_2):
    tc_obj = tc()
    tc.assertEqual(tc_obj, post_1.text, post_2.text)
    tc.assertEqual(tc_obj, post_1.author, post_2.author)
    tc.assertEqual(tc_obj, post_1.image, post_2.image)


def check_group(group_1, group_2):
    tc_obj = tc()
    tc.assertEqual(tc_obj, group_1.title, group_2.title)
    tc.assertEqual(tc_obj, group_1.description, group_2.dexcription)
