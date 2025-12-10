from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
import uuid

# Import models
from maquinaria.models import Maquina, AlertaMaquina, HistorialMaquina
from usuarios.models import Usuario
from reportes.models import Reporte

# Import serializers (we'll create these later)
from .serializers import (
    MaquinaSerializer, AlertaMaquinaSerializer,
    HistorialMaquinaSerializer
)

class MaquinaViewSet(viewsets.ModelViewSet):
    serializer_class = MaquinaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Maquina.objects.all()

        # Filtros opcionales
        categoria = self.request.query_params.get('categoria', None)
        estado = self.request.query_params.get('estado', None)
        centro = self.request.query_params.get('centro', None)

        if categoria:
            queryset = queryset.filter(categoria__nombre__icontains=categoria)
        if estado:
            queryset = queryset.filter(estado=estado)
        if centro:
            queryset = queryset.filter(centro_formacion__icontains=centro)

        return queryset.select_related('categoria', 'proveedor').order_by('codigo_inventario')

class AlertaMaquinaViewSet(viewsets.ModelViewSet):
    serializer_class = AlertaMaquinaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = AlertaMaquina.objects.all()

        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset.select_related('maquina').order_by('-fecha_creacion')

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            })
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Logout successful'})
        except:
            return Response({'error': 'Error during logout'},
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BuscarMaquinasAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')

        if len(query) < 2:
            return Response({'results': []})

        maquinas = Maquina.objects.filter(
            Q(nombre__icontains=query) |
            Q(codigo_inventario__icontains=query) |
            Q(marca__icontains=query) |
            Q(modelo__icontains=query)
        )[:10]

        serializer = MaquinaSerializer(maquinas, many=True)
        return Response({'results': serializer.data})

class HistorialMaquinaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        maquina = get_object_or_404(Maquina, pk=pk)
        historial = HistorialMaquina.objects.filter(maquina=maquina).order_by('-fecha_evento')[:20]
        serializer = HistorialMaquinaSerializer(historial, many=True)
        return Response(serializer.data)

class CambiarEstadoMaquinaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        maquina = get_object_or_404(Maquina, pk=pk)
        nuevo_estado = request.data.get('estado')

        if nuevo_estado not in dict(Maquina.ESTADO_CHOICES):
            return Response({
                'error': 'Estado no válido'
            }, status=status.HTTP_400_BAD_REQUEST)

        estado_anterior = maquina.estado
        maquina.estado = nuevo_estado
        maquina.save()

        # Crear registro en historial
        HistorialMaquina.objects.create(
            maquina=maquina,
            tipo_evento='cambio_estado',
            descripcion=f'Estado cambiado de {estado_anterior} a {nuevo_estado}',
            valor_anterior=estado_anterior,
            valor_nuevo=nuevo_estado,
            usuario=request.user
        )

        return Response({'message': 'Estado actualizado correctamente'})

class AlertasActivasAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        alertas = AlertaMaquina.objects.filter(
            estado='activa'
        ).order_by('-prioridad', '-fecha_creacion')[:10]

        serializer = AlertaMaquinaSerializer(alertas, many=True)
        return Response(serializer.data)

class ResolverAlertaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        alerta = get_object_or_404(AlertaMaquina, pk=pk)
        notas = request.data.get('notas', '')

        alerta.estado = 'resuelta'
        alerta.fecha_resolucion = timezone.now()
        alerta.resuelto_por = request.user
        alerta.notas_resolucion = notas
        alerta.save()

        return Response({'message': 'Alerta resuelta correctamente'})

class GenerarReporteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # TODO: Implementar generación de reportes
        return Response({
            'message': 'Generación de reportes en desarrollo'
        })

class DescargarReporteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # TODO: Implementar descarga de reportes
        return Response({
            'message': 'Descarga de reportes en desarrollo'
        })

class DatosDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Estadísticas básicas para el dashboard
        total_maquinas = Maquina.objects.count()
        maquinas_operativas = Maquina.objects.filter(estado='operativa').count()
        maquinas_mantenimiento = Maquina.objects.filter(estado='mantenimiento').count()
        alertas_activas = AlertaMaquina.objects.filter(estado='activa').count()

        return Response({
            'total_maquinas': total_maquinas,
            'maquinas_operativas': maquinas_operativas,
            'maquinas_mantenimiento': maquinas_mantenimiento,
            'alertas_activas': alertas_activas,
            'porcentaje_operativas': (maquinas_operativas / total_maquinas * 100) if total_maquinas > 0 else 0
        })

class ResumenMetricasAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: Implementar métricas más detalladas
        return Response({
            'eficiencia_promedio': 87.5,
            'tiempo_promedio_reparacion': 2.3,
            'costo_mantenimiento_mes': 245000,
            'satisfaccion_usuario': 94.2
        })

class EstadisticasGeneralesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: Implementar estadísticas generales
        return Response({
            'usuarios_activos': 25,
            'consultas_ia_mes': 156,
            'reportes_generados': 42,
            'documentos_subidos': 89
        })

class SystemStatusAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'status': 'ok',
            'timestamp': timezone.now(),
            'version': '1.0.0',
            'database': 'connected'
        })

class ImportarMaquinasAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # TODO: Implementar importación masiva
        return Response({
            'message': 'Importación masiva en desarrollo'
        })

class ExportarMaquinasAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: Implementar exportación masiva
        return Response({
            'message': 'Exportación masiva en desarrollo'
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def status_check(request):
    return Response({'status': 'Sistema SENA operativo', 'timestamp': timezone.now()})