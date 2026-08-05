from rest_framework import serializers

from accounts.serializers import UserBriefSerializer
from attendance.models import AttendanceRecord


class AttendanceRecordSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source='user',
        queryset=AttendanceRecord._meta.get_field('user').related_model.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = AttendanceRecord
        fields = (
            'id',
            'user',
            'user_id',
            'date',
            'check_in_time',
            'check_out_time',
            'status',
            'notes',
            'created_at',
        )
        read_only_fields = ('id', 'created_at')
