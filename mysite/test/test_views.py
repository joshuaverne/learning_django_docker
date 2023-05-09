import contextlib

from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AnonymousUser, User

# noinspection PyUnresolvedReferences
from gallery.views import new_gallery_piece, new_exhibition


@contextlib.contextmanager
def middleware(request):
    """Annotate a request object with a session"""
    s_middleware = SessionMiddleware(get_response=1)
    s_middleware.process_request(request)
    request.session.save()

    """Annotate a request object with a messages"""
    m_middleware = MessageMiddleware(get_response=1)
    m_middleware.process_request(request)
    request.session.save()
    yield request


class GalleryPieceFormViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="jacob", email="jacob@…", password="top_secret"
        )
        self.anonUser = AnonymousUser()
        self.good_title = 'x' * 500
        self.good_desc = 'x' * 1000

    def test_get_view_redirect(self):
        request = self.factory.get("/gallery/pieces/new")

        request.user = self.user

        response = new_gallery_piece(request)

        self.assertEqual(200, response.status_code)

    def test_create_piece(self):
        with open("test/images/woody.jpg", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': self.good_title,
                              'pieceDescription': self.good_desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/new", test_post_data)

            request.user = self.user

            with middleware(request):
                response = new_gallery_piece(request)

        self.assertEqual(302, response.status_code)

    def test_create_piece_anonymous_user(self):
        with open("test/images/woody.jpg", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': self.good_title,
                              'pieceDescription': self.good_desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/new", test_post_data)

            request.user = self.anonUser

            response = new_gallery_piece(request)

        self.assertEqual(405, response.status_code)

    def test_create_piece_title_too_long(self):
        title = "x" * 501

        with open("test/images/woody.jpg", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': title,
                              'pieceDescription': self.good_desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/new", test_post_data)

            request.user = self.user

            response = new_gallery_piece(request)

        self.assertEqual(400, response.status_code)

    def test_create_piece_description_too_long(self):
        desc = "x" * 1001

        with open("test/images/woody.jpg", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': self.good_title,
                              'pieceDescription': desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/new", test_post_data)

            request.user = self.user

            response = new_gallery_piece(request)

        self.assertEqual(400, response.status_code)

    def test_create_piece_image_too_large(self):
        with open("test/images/city.jpg", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': self.good_title,
                              'pieceDescription': self.good_desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/new", test_post_data)

            request.user = self.user

            response = new_gallery_piece(request)

        self.assertEqual(400, response.status_code)

    def test_create_piece_wrong_image_type(self):
        with open("test/images/dragon.gif", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': self.good_title,
                              'pieceDescription': self.good_desc,
                              'pieceImage': fp}

            request = self.factory.post("/gallery/pieces/new", test_post_data)

            request.user = self.user

            response = new_gallery_piece(request)

        self.assertEqual(400, response.status_code)


class ExhibitionFormViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="jacob", email="jacob@…", password="top_secret"
        )
        self.anonUser = AnonymousUser()
        self.good_title = 'x' * 200
        self.good_desc = 'x' * 1000

    def test_create_exhibition(self):
        test_post_data = {'placeholder': "PLACEHOLDER",
                          'exhibitionTitle': self.good_title,
                          'exhibitionDescription': self.good_desc}

        request = self.factory.post("/gallery/exhibitions/new", test_post_data)
        request.user = self.user

        with middleware(request):
            response = new_exhibition(request)

        self.assertEqual(302, response.status_code)

    def test_create_exhibition_anonymous_user(self):
        test_post_data = {'placeholder': "PLACEHOLDER",
                          'exhibitionTitle': self.good_title,
                          'exhibitionDescription': self.good_desc}

        request = self.factory.post("/gallery/exhibitions/new", test_post_data)
        request.user = self.anonUser

        with middleware(request):
            response = new_exhibition(request)

        self.assertEqual(405, response.status_code)

    def test_create_exhibition_title_too_long(self):
        long_title = 'x' * 201

        test_post_data = {'placeholder': "PLACEHOLDER",
                          'exhibitionTitle': long_title,
                          'exhibitionDescription': self.good_desc}

        request = self.factory.post("/gallery/exhibitions/new", test_post_data)
        request.user = self.user

        with middleware(request):
            response = new_exhibition(request)

        self.assertEqual(400, response.status_code)

    def test_create_exhibition_description_too_long(self):
        long_desc = 'x' * 1001

        test_post_data = {'placeholder': "PLACEHOLDER",
                          'exhibitionTitle': self.good_title,
                          'exhibitionDescription': long_desc}

        request = self.factory.post("/gallery/exhibitions/new", test_post_data)
        request.user = self.user

        with middleware(request):
            response = new_exhibition(request)

        self.assertEqual(400, response.status_code)
