"""Serializers for the InventoryOne API."""
from rest_framework import serializers

from .models import (
    Broker,
    Plot,
    Project,
)


class PlotSerializer(serializers.ModelSerializer):
    total_cost = serializers.SerializerMethodField()
    facing_display = serializers.CharField(source='get_facing_display', read_only=True)

    class Meta:
        model = Plot
        fields = [
            'id', 'plot_number', 'size_sq_yds', 'facing', 'facing_display', 'status',
            'bsp', 'plc_pct', 'discount_pct', 'total_cost',
        ]

    def get_total_cost(self, obj):
        return obj.total_cost


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'code', 'location', 'status', 'description', 'created_at']


class ProjectListSerializer(ProjectSerializer):
    total_plots = serializers.IntegerField(read_only=True)
    available = serializers.IntegerField(read_only=True)
    on_hold = serializers.IntegerField(read_only=True)
    sold = serializers.IntegerField(read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['total_plots', 'available', 'on_hold', 'sold']


class ProjectDetailSerializer(ProjectSerializer):
    plots = PlotSerializer(many=True, read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['plots']


class BrokerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    name = serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = Broker
        fields = ['id', 'email', 'name', 'phone', 'kyc_status', 'pan_number',
                  'aadhaar_number', 'gst_number', 'rera_number', 'bank_account',
                  'ifsc', 'agreement_accepted', 'created_at']
        read_only_fields = ['id', 'email', 'name', 'kyc_status', 'created_at']
