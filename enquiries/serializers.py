from rest_framework import serializers

from .models import Enquiry


class EnquirySerializer(serializers.ModelSerializer):
    # Honeypot: the form renders this hidden and off-screen, so a human never
    # fills it. Bots that fill every input give themselves away.
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Enquiry
        fields = ["id", "name", "business", "email", "phone", "package", "message", "website", "created_at"]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "name": {"trim_whitespace": True},
            "business": {"trim_whitespace": True},
            "phone": {"trim_whitespace": True},
        }

    def validate_website(self, value):
        if value.strip():
            # Deliberately vague: don't tell a bot which field caught it.
            raise serializers.ValidationError("This enquiry could not be accepted.")
        return value

    def validate_message(self, value):
        # A form this small has no reason to carry an essay; caps DB abuse.
        if len(value) > 4000:
            raise serializers.ValidationError("Please keep the project details under 4000 characters.")
        return value

    def create(self, validated_data):
        validated_data.pop("website", None)
        return super().create(validated_data)