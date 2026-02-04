from rest_framework import serializers
from addresses.models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "name",
            "mobile",
            "address_line",
            "city",
            "state",
            "pincode",
            "is_default",
        ]