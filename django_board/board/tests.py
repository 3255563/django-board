from tempfile import TemporaryFile

from django.test import TestCase
from django.core.files.base import ContentFile

from PIL import Image

from .models import Thread, Reply


def create_temporary_picture(size=(100, 100),
                             color=(255, 0, 0), img_type='png'):
    """Creates a temporary picture for testing file upload.
    Returns a Django ContentFile object."""
    image_file = TemporaryFile()
    image = Image.new('RGBA', size, color)
    image.save(image_file, img_type)
    image_file.seek(0)
    return(ContentFile(image_file.read(), 'test.png'))


class ThreadModelTests(TestCase):
    """Tests for the Thread model."""

    def test_create_thread_with_text_only(self):
        text = "thread created by the " \
            "test_create_thread_with_text_only() function"
        thread = Thread.objects.create(text=text)

        self.assertEqual(thread.text, text)

    def test_create_thread_with_all_fields_but_picture(self):
        name = "Tester"
        subj = "Testing"
        text = "thread created by the" \
            "test_create_thread_with_all_fields_but_picture() function"

        thread = Thread.objects.create(name=name, subj=subj, text=text)

        self.assertEqual(thread.name, name)
        self.assertEqual(thread.subj, subj)
        self.assertEqual(thread.text, text)

    def test_create_thread_with_picture(self):
        pic = create_temporary_picture()
        text = "thread created by the " \
            "test_create_thread_with_picture() function"
        thread = Thread.objects.create(text=text, picture=pic)

        pic.seek(0)
        self.assertEqual(thread.picture.read(), pic.read())

        # clean up after testing
        thread.picture.delete()

    def test_threads_id_incrementing(self):
        text = "thread {} created by the " \
            "test_threads_id_incrementing() function"

        thread1 = Thread.objects.create(text=text.format("No.1"))
        thread2 = Thread.objects.create(text=text.format("No.2"))

        self.assertEqual(thread2.id, thread1.id + 1)


class ReplyModelTests(TestCase):
    """Tests for the Reply model."""

    def test_create_thread_with_text_only_reply(self):
        thread_text = "thread created by the " \
            "test_create_thread_with_text_only_reply() function"
        thread = Thread.objects.create(text=thread_text)

        reply_text = "Reply to the " + thread_text
        reply = thread.reply_set.create(text=reply_text)

        self.assertEqual(thread.reply_set.last().text, reply_text)
        self.assertEqual(thread.reply_set.last().id, thread.id + 1)

    def test_create_thread_and_reply_with_picture(self):
        thread_text = "thread created by the " \
            "test_create_thread_and_reply_with_picture() function"
        thread = Thread.objects.create(text=thread_text)

        reply_text = "Reply to the " + thread_text
        reply_pic = create_temporary_picture()
        reply = thread.reply_set.create(text=reply_text, picture=reply_pic)
        reply_pic.seek(0)

        self.assertEqual(reply.picture.read(), reply_pic.read())
