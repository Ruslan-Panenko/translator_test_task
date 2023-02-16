import uuid, json
import firebase_admin
from django.conf import settings
from django.http import HttpResponse
from firebase_admin import credentials, auth, firestore
from django.views.decorators.csrf import csrf_exempt

firebase = credentials.Certificate(settings.FIREBASE_AUTH)
firebase_app = firebase_admin.initialize_app(firebase)
db = firestore.client()


def verify(request):
    header = request.META.get('HTTP_AUTHORIZATION')
    token = header.replace('Bearer ', '')
    decode_token = auth.verify_id_token(token)
    if not decode_token: raise Exception('Not valid token')
    return decode_token


@csrf_exempt
def translations(request):
    user = verify(request)
    if request.method == 'GET':
        users_ref = db.collection(u'translations')
        docs = users_ref.stream()

        result = [{doc.id: doc.to_dict()} for doc in docs]

        return HttpResponse([result], status=200)

    elif request.method == 'POST':
        input_text = json.loads(request.body)['input_text']
        output_text = json.loads(request.body)['output_text']
        new_object = db.collection(u'translations').document(f'translation {uuid.uuid4()}')
        new_object.set({
            'input_text': input_text,
            'output_text': output_text,
            'from_user': user['email']
        })
        return HttpResponse(request.body, status=201)


@csrf_exempt
def translation(request, pk):
    user = verify(request)
    doc_ref = db.collection(u'translations').document(pk)

    if request.method == 'GET':
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            if data['from_user'] != user['email']:
                return HttpResponse('Forbidden', status=403)
            data['id'] = doc.id
            return HttpResponse(json.dumps(data), status=200)
        else:
            return HttpResponse('Not Found', status=404)

    elif request.method == 'PUT':
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            if data['from_user'] != user['email']:
                return HttpResponse('Forbidden', status=403)
            input_text = json.loads(request.body)['input_text']
            output_text = json.loads(request.body)['output_text']
            doc_ref.set({
                'input_text': input_text,
                'output_text': output_text,
                'from_user': user['email']
            }, merge=True)
            return HttpResponse(request.body, status=200)
        else:
            return HttpResponse('Not Found', status=404)

    elif request.method == 'DELETE':
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            if data['from_user'] != user['email']:
                return HttpResponse('Forbidden', status=403)
            doc_ref.delete()
            return HttpResponse(status=204)
        else:
            return HttpResponse('Not Found', status=404)