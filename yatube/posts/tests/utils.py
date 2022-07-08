from django.test import TestCase as tc


def check_post(post_1, post_2, **data):
    tc_obj = tc()
    tc.assertEqual(tc_obj, post_1.text, data['text'])
    tc.assertEqual(tc_obj, post_1.group_id, data['group'])
    tc.assertEqual(tc_obj, post_1.author, post_2.author)
