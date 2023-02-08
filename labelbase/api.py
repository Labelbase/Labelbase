
from labelbase.models import Labelbase, Label
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework import status
#from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView



class LabelbaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labelbase
        fields = ('id', 'name', 'fingerprint', 'about', )
        read_only_fields = ('id', )


class LabelbaseAPIView(APIView):
    """
    Retrieve, update or delete a labelbases.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def _get_labelbase(self, request, id):
        try:
            labelbase = Labelbase.objects.get(id=id, user_id=request.user.id)
            return labelbase
        except Labelbase.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        """
        Create the new labelbase.
        """
        print (request.data)
        data = {
            'name': request.data.get('name', ''),
            'fingerprint': request.data.get('fingerprint', ''),
            'about': request.data.get('about', ''),
            'user_id': request.user.id
        }
        serializer = LabelbaseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        """
        Update labelbase with the given id.
        """
        labelbase = get_object_or_404(Labelbase, id=id, user_id=request.user.id)
        serializer = LabelbaseSerializer(labelbase, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id):
        """
        Retrieve labelbase with the given id.
        """
        labelbase = self._get_labelbase(request, id)
        serializer = LabelbaseSerializer(labelbase)
        return Response(serializer.data)

    def delete(self, request, id):
        """
        Delete the labelbase with the given id.
        """
        labelbase = self._get_labelbase(request, id)
        labelbase.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('id', 'labelbase', 'type', 'ref', 'label', )
        read_only_fields = ('id', 'labelbase', )



class LabelAPIView(APIView):
    """
    Retrieve, update or delete a label.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def _get_label(self, request, labelbase_id, id):
        try:
            label = Label.objects.get(  id=id,
                                        labelbase_id=labelbase_id,
                                        labelbase__user_id=request.user.id)
            return label
        except Label.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, labelbase_id, *args, **kwargs):
        """
        Create the new label within a labelbase accessed by the given id.
        """
        data = {
            'labelbase_id': Labelbase.objects.get(id=labelbase_id, user_id=request.user.id).id,
            'type': request.data.get('type', ''),
            'ref': request.data.get('ref', ''),
            'label': request.data.get('label', ''),
        }
        serializer = LabelbaseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, labelbase_id, id):
        label = self._get_label(request, labelbase_id, id)
        serializer = LabelSerializer(label, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, labelbase_id, id):
        label = self._get_label(request, labelbase_id, id)
        serializer = LabelSerializer(label)
        return Response(serializer.data)

    def delete(self, request, labelbase_id, id):
        label = self._get_label(request, labelbase_id, id)
        label.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
