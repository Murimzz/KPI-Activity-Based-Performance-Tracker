from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import User, UserRole
from departments.models import Department


class DepartmentBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name')


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'employee_or_intern_number',
        )


class UserSerializer(serializers.ModelSerializer):
    department = DepartmentBriefSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        source='department',
        queryset=Department.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )
    supervisor = UserBriefSerializer(read_only=True)
    supervisor_id = serializers.PrimaryKeyRelatedField(
        source='supervisor',
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'role',
            'employee_or_intern_number',
            'department',
            'department_id',
            'supervisor',
            'supervisor_id',
            'phone_number',
            'is_active',
            'date_joined',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'date_joined', 'created_at', 'updated_at')


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    department_id = serializers.PrimaryKeyRelatedField(
        source='department',
        queryset=Department.objects.all(),
        allow_null=True,
        required=False,
    )
    supervisor_id = serializers.PrimaryKeyRelatedField(
        source='supervisor',
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'password',
            'role',
            'employee_or_intern_number',
            'department_id',
            'supervisor_id',
            'phone_number',
            'is_active',
        )
        read_only_fields = ('id',)

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, **validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    """Public/self registration limited to INTERN or STAFF roles."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'password',
            'password_confirm',
            'role',
            'employee_or_intern_number',
            'phone_number',
        )
        read_only_fields = ('id',)

    def validate_role(self, value):
        if value not in (UserRole.INTERN, UserRole.STAFF):
            raise serializers.ValidationError(
                'Self-registration is limited to INTERN or STAFF roles.'
            )
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError(
                {'password_confirm': 'Passwords do not match.'}
            )
        return attrs

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        validated_data.setdefault('role', UserRole.INTERN)
        return User.objects.create_user(password=password, **validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value, user=self.context['request'].user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT login using email + password (USERNAME_FIELD is email)."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['email'] = user.email
        token['full_name'] = user.get_full_name()
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
