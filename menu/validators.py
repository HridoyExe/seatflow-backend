from django.core.exceptions import ValidationError
def validate_image(image):
    max_size = 2 * 1024 * 1024  
    if image.size > max_size:
        raise ValidationError("Image size should be less than 2MB") 
    

    valid_extensions = ["jpg", "jpeg", "png", "webp"]
    ext = image.name.split(".")[-1].lower()

    if ext not in valid_extensions:
        raise ValidationError("Unsupported image format")