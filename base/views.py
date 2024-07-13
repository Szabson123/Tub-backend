from rest_framework import viewsets, status, generics, permissions
from .models import Tub, Reservation, Rating, Discount, Faq
from .serializers import TubSerializer, ReservationSerializer, RatingSerializer, DiscountSerializer, FaqSerializer, AddTubSerializer, Address, FaqQuestionSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from decimal import Decimal
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from custom_auth.serializers import UserSerializer
from custom_auth.models import CustomUser
from django.contrib.auth import get_user_model


class IsManager(permissions.BasePermission):
    """
    Custom permission to only allow managers to access certain views.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and is a manager
        return request.user and request.user.is_authenticated and request.user.is_manager


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserReservationHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        reservations = user.user_reservations.all()
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)


class SpecificUserProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id, *args, **kwargs):
        user = CustomUser.objects.get(pk=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class TubViewListSet(viewsets.ModelViewSet):
    queryset = Tub.objects.all()
    serializer_class = TubSerializer
    permission_classes = [AllowAny]


class AddTubView(generics.CreateAPIView):
    queryset = Tub.objects.all()
    serializer_class = AddTubSerializer
    permission_classes = [IsAuthenticated]


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['POST'])
    def create_reservation(self, request, pk=None):
        user = request.user if request.user.is_authenticated else None
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        address_data = {
            'city': request.data.get('city'),
            'street': request.data.get('street'),
            'home_number': request.data.get('home_number')
        }
        discount_id = request.data.get('discount_id')

        tub = get_object_or_404(Tub, pk=pk)

        if not start_date or not end_date:
            return Response({'message': 'Start Date and End Date are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Reservation.objects.filter(tub=tub, start_date__lte=end_date, end_date__gte=start_date).exists():
            return Response({'message': 'This tub is already reserved for the selected dates'}, status=status.HTTP_400_BAD_REQUEST)

        price = tub.price_per_day
        counted_price = Decimal(request.data.get('counted_price', price))  # Pobranie counted_price z requesta

        if discount_id:
            discount = get_object_or_404(Discount, pk=discount_id)
            
            if discount.tub != tub:
                return Response({'message': 'This is not the right code for this tub'}, status=status.HTTP_400_BAD_REQUEST)
        
            if not discount.active:
                return Response({'message': 'This code is not available'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not discount.is_multi_use and discount.used:
                return Response({'message': 'This code has already been used'}, status=status.HTTP_400_BAD_REQUEST)
            
            discount_value = Decimal(discount.value) / Decimal(100)
            counted_price = price * (Decimal(1) - discount_value)
            
            if not discount.is_multi_use:
                discount.used = True
                discount.active = False
            
            discount.save()

        reservation = Reservation.objects.create(
            user=user,
            tub=tub,
            price=price,
            counted_price=counted_price,
            start_date=start_date,
            end_date=end_date,
            wait_status=True
        )

        Address.objects.create(
            reservation=reservation,
            **address_data
        )

        response_data = {
            'message': 'Reservation created. Wait for acceptance by owner',
            'result': ReservationSerializer(reservation).data
        }

        if discount_id:
            response_data['message'] = 'Reservation created, discount applied successfully. Wait for acceptance by owner'
            response_data['discounted_price_per_day'] = counted_price
            response_data['original_price_per_day'] = price
            response_data['discount_value'] = f'{discount.value}%'

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['GET'])
    def check_reservations(self, request, pk=None):
        tub = get_object_or_404(Tub, pk=pk)
        reservations = Reservation.objects.filter(tub=tub)
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def all_reservations(self, request):
        reservations = Reservation.objects.all()
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PATCH'])
    def accept_reservation(self, request, pk=None):
        reservation = get_object_or_404(Reservation, pk=pk)
        reservation.wait_status = False
        reservation.accepted_status = True
        reservation.save()
        serializer = ReservationSerializer(reservation)
        return Response({'message': 'Reservation accepted', 'result': serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def accepted_reservations(self, request):
        reservations = Reservation.objects.filter(accepted_status=True)
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['DELETE'])
    def delete_reservation(self, request, pk=None):
        reservation = get_object_or_404(Reservation, pk=pk)
        reservation.delete()
        return Response({'message': 'Reservation deleted'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def pending_reservations(self, request):
        reservations = Reservation.objects.filter(accepted_status=False)
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
        
class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['POST'])
    def create_rating(self, request, pk=None):
        tub = get_object_or_404(Tub, pk=pk)
        user = self.request.user if request.user.is_authenticated else None
        stars = request.data.get('stars')
        
        if stars is not None:
            try:
                rating = Rating.objects.get(user=user, tub=tub)
                rating.stars = stars
                rating.save()
                serializer = RatingSerializer(rating, many=False)
                return Response({'message':'Rating updated', 'result': serializer.data}, status=status.HTTP_200_OK)
            except Rating.DoesNotExist:
                rating = Rating.objects.create(user=user, tub=tub, stars=stars)
                serializer = RatingSerializer(rating, many=False)
                return Response({'message': 'Rating Created', 'result': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'message':'You need to provide starts'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['GET'])
    def rating_list(self, request, pk=None):
        tub = get_object_or_404(Tub, pk=pk)
        rating = Rating.objects.filter(tub=tub)
        serializer = RatingSerializer(rating, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
                
class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [AllowAny]


class UserFaqQuestionView(generics.CreateAPIView):
    serializer_class = FaqQuestionSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ManagerFaqListView(generics.ListAPIView):
    serializer_class = FaqSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Faq.objects.all()

class PublishedFaqListView(generics.ListAPIView):
    serializer_class = FaqSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Faq.objects.filter(is_published=True)

class UpdateFaqStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def patch(self, request, pk):
        try:
            faq = Faq.objects.get(pk=pk)
            faq.is_published = not faq.is_published
            faq.save()
            return Response({'status': 'success', 'is_published': faq.is_published}, status=status.HTTP_200_OK)
        except Faq.DoesNotExist:
            return Response({'status': 'error', 'message': 'FAQ not found'}, status=status.HTTP_404_NOT_FOUND)


class FaqUpdateView(generics.UpdateAPIView):
    queryset = Faq.objects.all()
    serializer_class = FaqSerializer
    permission_classes = [AllowAny]