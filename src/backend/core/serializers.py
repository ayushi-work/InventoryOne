"""Serializers for the InventoryOne API."""
from rest_framework import serializers

from .models import Booking, Broker, Commission, Customer, Plot, Project


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


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'address', 'created_at']
        read_only_fields = ['id', 'created_at']


class BookingSerializer(serializers.ModelSerializer):
    broker = serializers.PrimaryKeyRelatedField(read_only=True)
    broker_name = serializers.CharField(source='broker.user.first_name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    plot_details = PlotSerializer(source='plot', read_only=True)
    commission = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['id', 'broker', 'broker_name', 'customer', 'customer_name',
                  'plot', 'plot_details', 'token_amount', 'payment_mode',
                  'commission_pct', 'status', 'created_at', 'decided_at', 'commission']
        read_only_fields = ['broker', 'status', 'created_at', 'decided_at']

    def get_commission(self, obj):
        try:
            return obj.commission.net_amount
        except Commission.DoesNotExist:
            return None


class CommissionSerializer(serializers.ModelSerializer):
    broker_id = serializers.IntegerField(source='broker.id', read_only=True)
    broker_name = serializers.CharField(source='broker.user.first_name', read_only=True)
    customer_name = serializers.CharField(source='booking.customer.name', read_only=True)
    plot_label = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='booking.plot.project.name', read_only=True)

    class Meta:
        model = Commission
        fields = ['id', 'booking', 'broker_id', 'broker_name', 'customer_name',
                  'plot_label', 'project_name', 'amount', 'tds_pct', 'tds_amount',
                  'net_amount', 'released', 'released_at', 'created_at']

    def get_plot_label(self, obj):
        return str(obj.booking.plot)
