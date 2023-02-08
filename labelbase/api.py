
from labelbase.models import Labelbase, Label
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework import status
#from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


from rest_framework.fields import CurrentUserDefault

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'labelbase', 'type', 'ref', 'label', ]
        read_only_fields = ['id', 'labelbase']

class LabelbaseSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(LabelbaseSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')

    class Meta:
        model = Labelbase
        fields = ['id', 'name', 'fingerprint', 'about',  ]
        read_only_fields = ['id', 'user', ]

    def create(self, validated_data):
        obj = Labelbase(**validated_data)
        obj.user_id = self.request.user.id
        obj.save()
        return obj


class LabelbaseAPIView(APIView):
    """
    Retrieve, update or delete a labelbases.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        """
        Create the new labelbase.
        """
        data = {
            'name': request.data.get('name', ''),
            'fingerprint': request.data.get('fingerprint', ''),
            'about': request.data.get('about', ''),
        }
        serializer = LabelbaseSerializer(data=data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        """
        Update labelbase with the given id.
        """
        labelbase = get_object_or_404(Labelbase, id=id, user_id=request.user.id)
        serializer = LabelbaseSerializer(labelbase, data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id):
        """
        Retrieve labelbase with the given id.
        """
        labelbase = get_object_or_404(Labelbase, id=id, user_id=request.user.id)
        serializer = LabelbaseSerializer(labelbase, context={'request':request})
        return Response(serializer.data)

    def delete(self, request, id):
        """
        Delete the labelbase with the given id.
        """
        labelbase = get_object_or_404(Labelbase, id=id, user_id=request.user.id)
        labelbase.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class LabelAPIView(APIView):
    """
    Retrieve, update or delete a label.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, labelbase_id, *args, **kwargs):
        """
        Create the new label within a labelbase accessed by the given id.
        """
        labelbase = get_object_or_404(Labelbase, id=labelbase_id, user_id=request.user.id)

        data = {
            'labelbase': labelbase.id,
            'type': request.data.get('type', 'addr'),
            'ref': request.data.get('ref', ''),
            'label': request.data.get('label', ''),
        }


        serializer = LabelSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, labelbase_id, id):
        label = get_object_or_404(Label, id=id, labelbase_id=labelbase_id, labelbase__user_id=request.user.id)
        data = {
            'labelbase': label.labelbase.id, # revents moving the label to another labelbase
            'type': request.data.get('type', 'addr'),
            'ref': request.data.get('ref', ''),
            'label': request.data.get('label', ''),
        }
        serializer = LabelSerializer(label, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, labelbase_id, id):
        label = get_object_or_404(Label, id=id, labelbase_id=labelbase_id, labelbase__user_id=request.user.id)

        serializer = LabelSerializer(label)
        return Response(serializer.data)

    def delete(self, request, labelbase_id, id):
        label = get_object_or_404(Label, id=id, labelbase_id=labelbase_id, labelbase__user_id=request.user.id)

        label.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
