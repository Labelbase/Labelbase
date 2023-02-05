
from labelbase.models import Labelbase, Label

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
        fields = ('id', 'name', 'fingerprint', 'about')
        read_only_fields = ('id')

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('id', 'labelbase', 'type', 'ref', 'label')
        read_only_fields = ('id', 'labelbase')

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

    def put(self, request, labelbase_id, id):
        label = self._get_label(request, labelbase_id, id)
        serializer = LabelSerializer(label, data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("OK, PUT {}".format(serializer.data))
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
