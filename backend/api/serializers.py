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


class HomeLocationSerializer(serializers.ModelSerializer):
    street = StreetSerializer()

    class Meta:
        model = Home
        fields = ['house_number', 'street']


class FlatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = ['flat_number', 'flat_size']


class StreetСreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Street
        fields = ['street_name']

    def to_internal_value(self, data):
        if isinstance(data, str):
            return {'street_name': data}
        return super().to_internal_value(data)


class HomeCreateUpdateSerializer(serializers.ModelSerializer):
    street = StreetСreateSerializer(required=False, allow_null=True)
    flats = FlatCreateSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Home
        fields = ['house_number', 'street', 'flats']

    def create(self, validated_data):
        street_data = validated_data.pop('street', None)
        flats_data = validated_data.pop('flats', [])

        if street_data:
            street, _ = Street.objects.get_or_create(**street_data)
        home, created = Home.objects.get_or_create(
            house_number=validated_data['house_number'],
            street=street, defaults=validated_data
        )
        if not created:
            for attr, value in validated_data.items():
                setattr(home, attr, value)
            home.save()
        for flat_data in flats_data:
            flat, created = Flat.objects.get_or_create(
                flat_number=flat_data['flat_number'],
                defaults=flat_data
            )
            if not created:
                flat.flat_size = flat_data['flat_size']
                flat.save()
            home.flats.add(flat)
        sorted_flats = sorted(home.flats.all(), key=lambda x: x.flat_number)
        home.flats.set(sorted_flats)

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
        existing_flats = {
            flat.flat_number: flat for flat in instance.flats.all()
        }
        new_flats = []
        for flat_data in flats_data:
            flat_number = flat_data.get('flat_number')
            if flat_number in existing_flats:
                flat = existing_flats[flat_number]
                flat.flat_size = flat_data.get('flat_size', flat.flat_size)
                flat.save()
            else:
                new_flat = Flat.objects.create(**flat_data)
                new_flats.append(new_flat)

        instance.flats.add(*new_flats)
        return instance
