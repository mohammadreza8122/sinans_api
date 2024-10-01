from rest_framework import serializers
from .models import User, UserAddress, RegisterCode, UserMessage , Complaint, HomeCareCompany
from cart.models import HomeCareOrder
from service.models import City
from jdatetime import datetime as jdatetime_datetime
from service.serializers import HomeCareCompanySerializer

class UserSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField()
    company_manager = serializers.SerializerMethodField()
    service_access = serializers.SerializerMethodField()
    order_access = serializers.SerializerMethodField()
    homecare = HomeCareCompanySerializer
    company = serializers.PrimaryKeyRelatedField(
        queryset=HomeCareCompany.objects.all(), required=False
    )
    first_company = serializers.PrimaryKeyRelatedField(
        queryset=HomeCareCompany.objects.all(), required=False
    )
    
    def get_manager(self, obj):
        if hasattr(obj, "manager"):
            if obj.manager.city:
                return [
                    {"id": city.id, "title": city.title}
                    for city in obj.manager.city.all()
                ]
            else:
                return None
        else:
            return None

    def get_company_manager(self, obj):
        if hasattr(obj, "company_manager"):
            if obj.company_manager.company:
                return {
                    "id": obj.company_manager.company.city.title,
                    "title": obj.company_manager.company.title,
                }
            else:
                return None
        else:
            return None

    def get_service_access(self, obj):
        if hasattr(obj, "manager"):
            return obj.manager.service_access

    def get_order_access(self, obj):
        if hasattr(obj, "manager"):
            return obj.manager.order_access

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "sex",
            "number",
            "email",
            "national_code",
            "image",
            "city",
            "province",
            "manager",
            "company_manager",
            "service_access",
            "order_access",
            "company",
            "first_company",
        )

        read_only_fields = ("number", "manager", "company_manager", "first_company")

    def validate_national_code(self, attrs):
        if attrs:
            if not attrs.isnumeric():
                raise serializers.ValidationError("کد ملی باید تماما عددی باشد")
        return attrs

    def validate_username(self, attrs):
        if not attrs:
            raise serializers.ValidationError("نام کاربری نمی تواند خالی باشد")
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if "company" in representation and representation["company"]:
            representation["company"] = {
                "title": instance.company.title,
                "id": instance.company.id,
                "city": {
                    "title": instance.company.city.title,
                    "id": instance.company.city.id,
                } if instance.company.city else None,
            }
        if "first_company" in representation and representation["first_company"]:
            representation["first_company"] = {
                "title": instance.first_company.title,
                "id": instance.first_company.id,
                "city": (
                    {
                        "title": instance.first_company.city.title,
                        "id": instance.first_company.city.id,
                    }
                    if instance.first_company.city
                    else None
                ),
            }    
        return representation


class UserNumberSerializer(serializers.Serializer):
    number = serializers.CharField()

    def validate_number(self, value):
        if len(value) != 11:
            raise serializers.ValidationError("شماره همراه باید 11 رقم باشد")
        return value


class LoginSerializer(serializers.Serializer):
    number = serializers.CharField(label="Number", write_only=True)
    otp = serializers.CharField(
        label="OTP",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    register_code = serializers.CharField(label="Register Code", allow_blank=True)

    def validate(self, attrs):
        number = attrs.get("number")
        otp = attrs.get("otp")
        register_code = attrs.get("register_code")

        if not number or not otp:
            msg = "شماره همراه و رمز یکبار مصرف ضروری هستند"
            raise serializers.ValidationError(msg, code="authorization")

        if len(number) != 11 or not number.startswith("0") or not number.isnumeric():
            raise serializers.ValidationError("شماره همراه نامعتبر است")

        if len(otp) != 6 or not otp.isnumeric():
            raise serializers.ValidationError("رمز یکبار مصرف نامعتبر است")

        if (
            register_code
            and not RegisterCode.objects.filter(code=register_code).exists()
        ):
            raise serializers.ValidationError("کد معرف وجود ندارد")

        return attrs


class CreatePasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField(
        label="رمز عبور",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    password2 = serializers.CharField(
        label="تکرار رمز عبور",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, data):
        password1 = data.get("password1")
        password2 = data.get("password2")

        if len(password1) < 8:
            raise serializers.ValidationError("رمز شما باید حداقل 8 کاراکتر باشد")

        if password1 != password2:
            raise serializers.ValidationError("رمز ها مطابقت ندارند")
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        label="رمز قبلی",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
        required=True,
    )
    password1 = serializers.CharField(
        label="رمز جدید",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
        required=True,
    )
    password2 = serializers.CharField(
        label="تکرار رمز جدید",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
        required=True,
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("رمز قبلی اشتباه وارد شده")
        return value

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["password1"])
        user.save()


class LoginPasswordSerializer(serializers.Serializer):
    number = serializers.CharField(label="شماره", write_only=True)
    password = serializers.CharField(
        label="رمز",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        number = attrs.get("number")
        password = attrs.get("password")

        if not number or not password:
            msg = "شماره همراه و رمز ضروری هستند"
            raise serializers.ValidationError(msg, code="authorization")

        if len(number) != 11 or not number.startswith("0") or not number.isnumeric():
            raise serializers.ValidationError("شماره همراه نامعتبر است")

        return attrs


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = (
            "id",
            "title",
            "name",
            "province",
            "city",
            "address",
            "zip_code",
            "number",
        )

    def validate(self, attrs):
        number = attrs.get("number")
        zip_code = attrs.get("zip_code")

        if number:
            if (
                len(number) != 11
                or not number.startswith("0")
                or not number.isnumeric()
            ):
                raise serializers.ValidationError("شماره همراه نامعتبر است")

        if zip_code:
            if len(zip_code) != 10 or not zip_code.isnumeric():
                raise serializers.ValidationError("کدپستی نامعتبر است")

        return attrs


class UserMessageSerializer(serializers.ModelSerializer):
    persian_date = serializers.SerializerMethodField()

    def get_persian_date(self, obj):
        jalali_date = jdatetime_datetime.fromgregorian(datetime=obj.date_created)
        return {
            "date": f"{jalali_date.year}/{jalali_date.month}/{jalali_date.day}",
            "time": f"{jalali_date.hour}:{jalali_date.minute}",
        }

    class Meta:
        model = UserMessage
        exclude = ("date_created", "user")


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ["seen", "issue", "email_phone", "text"]

    def create(self, validated_data):
        
        return Complaint.objects.create(**validated_data)
        
        
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'title']
        
        
class HomeCareOrderSerializer(serializers.ModelSerializer): #new
    user = UserSerializer()
    city = CitySerializer()
    class Meta:
        model = HomeCareOrder
        fields = [
            'id',
            'user',
            'city',
            'date_created',
            'status',
            'pay_token',
            'final_price',
            'is_paid',
            'is_done',
            'due_date',
            'due_time',
            'due_date_time',
        ]

class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'number']