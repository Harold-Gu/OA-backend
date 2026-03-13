from rest_framework import serializers
from django.core.validators import FileExtensionValidator, get_available_image_extensions


class UploadImageSerializer(serializers.Serializer):
    # ImageField: Will verify whether the uploaded file is an image
    # .png/.jpeg/jpg
    image = serializers.ImageField(
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'gif'])],
        error_messages={'required': 'Please upload an image!', 'invalid_image': 'Please upload an image in the correct format!'}
    )

    def validate_image(self, value):
        # The unit of image size is bytes.
        # 1024B: 1KB
        # 1024KB: 1MB
        max_size = 0.5 * 1024 * 1024
        size = value.size
        if size > max_size:
            raise serializers.ValidationError('The size of the image must not exceed 0.5MB!')
        return value