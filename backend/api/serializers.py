from rest_framework import serializers

from home.models import Street, Flat, WaterChecker, Home


class StreetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Street
        fields = ['street_name']


class WaterCheckerSerializer(serializers.ModelSerializer):
    home = serializers.SlugRelatedField(slug_field='house_number',
                                        queryset=Home.objects.all()
                                        )
    flat = serializers.SlugRelatedField(slug_field='flat_number',
                                        queryset=Flat.objects.all()
                                        )

    class Meta:
        model = WaterChecker
        fields = ['home', 'flat', 'year', 'month', 'water_amount']


class FlatSerializer(serializers.ModelSerializer):
    water_checkers_count = serializers.SerializerMethodField()

    class Meta:
        model = Flat
        fields = ['flat_number', 'flat_size', 'water_checkers_count']

    def get_water_checkers_count(self, obj):
        total_records = WaterChecker.objects.filter(flat=obj).count()
        unique_months = WaterChecker.objects.filter(
            flat=obj
            ).values('year', 'month').distinct().count()
        if unique_months > 0:
            return total_records // unique_months
        return 0


class HomeSerializer(serializers.ModelSerializer):
    street = StreetSerializer(read_only=True)
    flats = FlatSerializer(many=True, read_only=True)

    class Meta:
        model = Home
        fields = ['house_number', 'street', 'flats']


class FlatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = ['flat_number', 'flat_size']


class HomeCreateUpdateSerializer(serializers.ModelSerializer):
    street = StreetSerializer(required=False, allow_null=True)
    flats = FlatCreateSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Home
        fields = ['house_number', 'street', 'flats']

    def create(self, validated_data):
        street_data = validated_data.pop('street', None)
        flats_data = validated_data.pop('flats', [])

        home = Home.objects.create(**validated_data)

        if street_data:
            street, _ = Street.objects.get_or_create(**street_data)
            home.street = street
            home.save()

        for flat_data in flats_data:
            flat, _ = Flat.objects.get_or_create(**flat_data)
            home.flats.add(flat)

        return home

    def update(self, instance, validated_data):
        street_data = validated_data.pop('street', None)
        flats_data = validated_data.pop('flats', [])
        instance.house_number = validated_data.get('house_number',
                                                   instance.house_number
                                                   )
        instance.save()
        if street_data:
            street, _ = Street.objects.get_or_create(**street_data)
            instance.street = street
            instance.save()
        existing_flats = set(instance.flats.all())
        new_flats = set()

        for flat_data in flats_data:
            flat, _ = Flat.objects.get_or_create(**flat_data)
            new_flats.add(flat)
        for flat in new_flats:
            if flat not in existing_flats:
                instance.flats.add(flat)
        return instance
