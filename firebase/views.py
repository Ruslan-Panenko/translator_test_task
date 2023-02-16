import uuid
import firebase_admin

from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from firebase_admin import credentials, auth, firestore
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, HttpResponseForbidden

firebase = credentials.Certificate(settings.FIREBASE_AUTH)
firebase_app = firebase_admin.initialize_app(firebase)
db = firestore.client()


def verify(request):
    header = request.META.get('HTTP_AUTHORIZATION')
    if not header: return None
    token = header.replace('Bearer ', '')
    try:
        decode_token = auth.verify_id_token(token)
    except:
        return None
    return decode_token


class TranslationsListAPIView(APIView):

    def get(self, request):
        if not verify(request):
            return HttpResponseForbidden('Not valid token')
        users_ref = db.collection(u'translations')
        docs = users_ref.stream()
        result = []
        for doc in docs:
            obj = doc.to_dict()
            obj['id'] = doc.id
            result.append(obj)
        return Response(result, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['input_text', 'output_text'],
        properties={
            'input_text': openapi.Schema(type=openapi.TYPE_STRING),
            'output_text': openapi.Schema(type=openapi.TYPE_STRING),
        },
    ))
    def post(self, request):
        user = verify(request)
        if not user: return HttpResponseForbidden('Not valid token')
        input_text = request.data['input_text']
        output_text = request.data['output_text']
        new_object = db.collection(u'translations').document(str(uuid.uuid4()))
        new_object.set({
            'input_text': input_text,
            'output_text': output_text,
            'from_user': user['email']
        })
        return Response(request.data, status=status.HTTP_201_CREATED)


class TranslationDetailAPIView(APIView):
    def get(self, request, pk):
        user = verify(request)
        if not user: return HttpResponseForbidden('Not valid token')

        doc_ref = db.collection(u'translations').document(pk)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            if data['from_user'] != user['email']:
                return HttpResponseForbidden('Forbidden')
            data['id'] = doc.id
            return Response(data, status=status.HTTP_200_OK)
        return HttpResponse('Not Found', status=404)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['input_text', 'output_text'],
        properties={
            'input_text': openapi.Schema(type=openapi.TYPE_STRING),
            'output_text': openapi.Schema(type=openapi.TYPE_STRING),
        },
    ))
    def put(self, request, pk):
        user = verify(request)
        if not user: return HttpResponseForbidden('Not valid token')

        doc_ref = db.collection(u'translations').document(pk)

        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            if data['from_user'] != user['email']:
                return HttpResponseForbidden('Forbidden')
            input_text = request.data['input_text']
            output_text = request.data['output_text']
            doc_ref.set({
                'input_text': input_text,
                'output_text': output_text,
                'from_user': user['email']
            }, merge=True)
            return Response(request.data, status=status.HTTP_200_OK)
        else:
            return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        user = verify(request)
        if not user: return HttpResponseForbidden('Not valid token')

        doc_ref = db.collection(u'translations').document(pk)

        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            if data['from_user'] != user['email']:
                return HttpResponseForbidden('Forbidden')
            doc_ref.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response('Not Found', status=status.HTTP_404_NOT_FOUND)
