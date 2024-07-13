from rest_framework import serializers
from .models import Tub, Image, Reservation, Rating, Discount, Faq, Address


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']


class TubSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    class Meta:
        model = Tub
        fields = ['id', 'name', 'description', 'price_per_day', 'price_per_week', 'images', 'logo_img']


class AddTubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tub
        fields = ['id', 'name', 'description', 'price_per_day', 'price_per_week', 'logo_img']


class RatingSerializer(serializers.ModelSerializer):
    tub_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Rating
        fields = ['id', 'tub_name', 'user', 'stars', 'desciption']
        
    def get_tub_name(self, obj):
        return obj.tub.name
    

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['tub', 'main', 'active', 'used', 'is_multi_use', 'value']
        

class FaqQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ['id', 'question'] 

class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ['id', 'question', 'answer', 'is_published']
        

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['city', 'street', 'home_number']

class ReservationSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ['id', 'tub', 'user', 'price', 'counted_price', 'start_date', 'end_date', 'nobody_status', 'wait_status', 'accepted_status', 'address']

    def get_address(self, obj):
        address = Address.objects.filter(reservation=obj).first()
        if address:
            return AddressSerializer(address).data
        return None

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        reservation = Reservation.objects.create(**validated_data)
        Address.objects.create(reservation=reservation, **address_data)
        return reservation