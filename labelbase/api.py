
from labelbase.models import Labelbase, Label

from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response



class LabelbaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labelbase
        fields = ('id', 'name', 'fingerprint', 'about')
        read_only_fields = ('id')

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('id', 'labelbase', 'type', 'ref', 'label', 'data')
        read_only_fields = ('id', 'labelbase')

@api_view(['GET', 'PUT', 'DELETE'])
def label(request, labelbase_id, id):
    """
    Retrieve, update or delete a label.
    """
    try:
        label = Label.objects.get(  id=id,
                                    labelbase_id=labelbase_id,
                                    labelbase__user_id=request.user.id)
    except Label.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LabelSerializer(label)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = LabelSerializer(label, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        label.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
