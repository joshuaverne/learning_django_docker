import contextlib, shutil, tempfile

from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase, override_settings
from django.contrib.auth.models import AnonymousUser, User

# noinspection PyUnresolvedReferences
from gallery.views import new_gallery_piece, new_exhibition, delete_gallery_piece, edit_gallery_piece
# noinspection PyUnresolvedReferences
from gallery.models import GalleryPiece

EXHIB_TITLE_MAX_LEN = 200
EXHIB_DESC_MAX_LEN = 1000

MEDIA_ROOT = tempfile.mktemp()

NON_AUTHENTICATED_STATUS_CODE = 401


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


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class GalleryPieceCreateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

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

        all_pieces = GalleryPiece.objects.all()
        for p in all_pieces:
            self.assertEqual(self.user, p.user)
            self.assertEqual(self.good_title, p.title)
            self.assertEqual(self.good_desc, p.description)

    def test_create_piece_anonymous_user(self):
        with open("test/images/woody.jpg", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': self.good_title,
                              'pieceDescription': self.good_desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/new", test_post_data)

            request.user = self.anonUser

            response = new_gallery_piece(request)

        self.assertEqual(NON_AUTHENTICATED_STATUS_CODE, response.status_code)

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


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class GalleryPieceDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="jacob", email="jacob@…", password="top_secret"
        )
        self.anonUser = AnonymousUser()
        self.good_title = 'x' * 500
        self.good_desc = 'x' * 1000

        with open("test/images/woody.jpg", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': self.good_title,
                              'pieceDescription': self.good_desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/new", test_post_data)

            request.user = self.user

            with middleware(request):
                new_gallery_piece(request)

        self.piece = GalleryPiece.objects.all()[0]
        self.piece_id = self.piece.id

    def test_delete_piece(self):
        self.assertEqual(1, len(GalleryPiece.objects.all()))

        request = self.factory.get("/gallery/exhibitions/" + str(self.piece_id) + "/delete")
        request.user = self.user

        with middleware(request):
            response = delete_gallery_piece(request, self.piece_id)

        self.assertEqual(302, response.status_code)

        self.assertEqual(0, len(GalleryPiece.objects.all()))

    def test_delete_piece_anonymous_user(self):
        self.assertEqual(1, len(GalleryPiece.objects.all()))

        request = self.factory.get("/gallery/exhibitions/" + str(self.piece_id) + "/delete")
        request.user = self.anonUser

        with middleware(request):
            response = delete_gallery_piece(request, self.piece_id)

        self.assertEqual(NON_AUTHENTICATED_STATUS_CODE, response.status_code)

        self.assertEqual(1, len(GalleryPiece.objects.all()))

    def test_delete_piece_wrong_user(self):
        self.assertEqual(1, len(GalleryPiece.objects.all()))

        request = self.factory.get("/gallery/exhibitions/" + str(self.piece_id) + "/delete")
        request.user = User.objects.create_user(
            username="jacob2", email="jacob2@…", password="top2_secret"
        )

        with middleware(request):
            response = delete_gallery_piece(request, self.piece_id)

        self.assertEqual(401, response.status_code)

        self.assertEqual(1, len(GalleryPiece.objects.all()))


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class GalleryPieceEditTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="jacob", email="jacob@…", password="top_secret"
        )
        self.anonUser = AnonymousUser()
        self.good_title = 'x' * 500
        self.good_desc = 'x' * 1000

        with open("test/images/woody.jpg", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': self.good_title,
                              'pieceDescription': self.good_desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/new", test_post_data)

            request.user = self.user

            with middleware(request):
                new_gallery_piece(request)

        self.piece = GalleryPiece.objects.all()[0]
        self.piece_id = self.piece.id
        self.img_url = self.piece.image.url

    def test_edit_all_fields(self):
        self.assert_initial_values(self.piece)

        new_title = "New title!"
        new_desc = "New description!"

        with open("test/images/scream.jpg", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': new_title,
                              'pieceDescription': new_desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/" + str(self.piece_id) + "/edit", test_post_data)

            request.user = self.user

            with middleware(request):
                response = edit_gallery_piece(request, self.piece_id)

        self.assertEquals(200, response.status_code)
        self.assertEquals(1, len(GalleryPiece.objects.all()))
        edited_piece = GalleryPiece.objects.all()[0]
        self.assertEquals(new_title, edited_piece.title)
        self.assertEquals(new_desc, edited_piece.description)
        self.assertTrue("scream" in edited_piece.image.url)

    def test_edit_bad_title(self):
        self.assert_initial_values(self.piece)

        new_title = "x" * 501
        new_desc = "New description!"

        with open("test/images/scream.jpg", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': new_title,
                              'pieceDescription': new_desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/" + str(self.piece_id) + "/edit", test_post_data)

            request.user = self.user

            with middleware(request):
                response = edit_gallery_piece(request, self.piece_id)

        self.assertEquals(200, response.status_code)
        edited_piece = GalleryPiece.objects.all()[0]
        self.assert_initial_values(edited_piece)

    def test_edit_bad_description(self):
        self.assert_initial_values(self.piece)

        new_title = "New title!"
        new_desc = "x" * 1001

        with open("test/images/scream.jpg", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': new_title,
                              'pieceDescription': new_desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/" + str(self.piece_id) + "/edit", test_post_data)

            request.user = self.user

            with middleware(request):
                response = edit_gallery_piece(request, self.piece_id)

        self.assertEquals(200, response.status_code)
        edited_piece = GalleryPiece.objects.all()[0]
        self.assert_initial_values(edited_piece)

    def test_edit_bad_image(self):
        self.assert_initial_values(self.piece)

        new_title = "New title!"
        new_desc = "New description!"

        # image is wrong file type
        with open("test/images/dragon.gif", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': new_title,
                              'pieceDescription': new_desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/" + str(self.piece_id) + "/edit", test_post_data)

            request.user = self.user

            with middleware(request):
                response = edit_gallery_piece(request, self.piece_id)

        self.assertEquals(200, response.status_code)
        edited_piece = GalleryPiece.objects.all()[0]
        self.assert_initial_values(edited_piece)

        # image is too large
        with open("test/images/city.jpg", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': new_title,
                              'pieceDescription': new_desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/" + str(self.piece_id) + "/edit", test_post_data)

            request.user = self.user

            with middleware(request):
                response = edit_gallery_piece(request, self.piece_id)

        self.assertEquals(200, response.status_code)
        edited_piece = GalleryPiece.objects.all()[0]
        self.assert_initial_values(edited_piece)

    def test_edit_anonymous_user(self):
        self.assert_initial_values(self.piece)

        new_title = "New title!"
        new_desc = "New description!"

        with open("test/images/scream.jpg", "rb") as fp:
            test_post_data = {'placeholder': "PLACEHOLDER",
                              'pieceTitle': new_title,
                              'pieceDescription': new_desc,
                              'pieceImage': fp}
            request = self.factory.post("/gallery/pieces/" + str(self.piece_id) + "/edit", test_post_data)

            request.user = self.anonUser

            with middleware(request):
                response = edit_gallery_piece(request, self.piece_id)

        self.assertEquals(NON_AUTHENTICATED_STATUS_CODE, response.status_code)
        edited_piece = GalleryPiece.objects.all()[0]
        self.assert_initial_values(edited_piece)

    def assert_initial_values(self, checked_piece):
        self.assertEquals(self.good_title, checked_piece.title)
        self.assertEquals(self.good_desc, checked_piece.description)
        self.assertEquals(self.img_url, checked_piece.image.url)


class ExhibitionFormViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="jacob", email="jacob@…", password="top_secret"
        )
        self.anonUser = AnonymousUser()
        self.good_title = 'x' * EXHIB_TITLE_MAX_LEN
        self.good_desc = 'x' * EXHIB_DESC_MAX_LEN

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

        self.assertEqual(NON_AUTHENTICATED_STATUS_CODE, response.status_code)

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


class ExhibitionEditTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="jacob", email="jacob@…", password="top_secret"
        )
        self.anonUser = AnonymousUser()
        self.good_title = 'x' * EXHIB_TITLE_MAX_LEN
        self.good_desc = 'x' * EXHIB_DESC_MAX_LEN
