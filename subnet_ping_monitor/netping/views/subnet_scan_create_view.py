from rest_framework import generics, status
from rest_framework.response import Response
from netping.models.subnet_request import SubnetRequest
from netping.serializers.subnet_request_serializer import SubnetRequestSerializer
from netping.tasks.start_ping_scan_task import start_ping_scan
from netping.utils.ip_helpers import InvalidSubnetException, get_ip_list


class SubnetScanCreateView(generics.CreateAPIView):
    queryset = SubnetRequest.objects.all()
    serializer_class = SubnetRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                get_ip_list(serializer.validated_data['ip_network'])
            except InvalidSubnetException as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            subnet = serializer.save()
            start_ping_scan.delay(subnet.id)

            return Response({
                'message': 'Ping taraması başlatıldı.',
                'subnet_id': subnet.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)