from django.contrib import admin, messages
from django.utils import timezone
from django.db import transaction
from ..models.treasury import RepresentativeVault, CollectionAction, CompanyTreasury

@admin.register(RepresentativeVault)
class RepresentativeVaultAdmin(admin.ModelAdmin):
    list_display = ('representative', 'current_cash_balance', 'last_clearance_date')
    readonly_fields = ('current_cash_balance', 'last_clearance_date')
    search_fields = ('representative__username', 'representative__first_name')

@admin.register(CollectionAction)
class CollectionActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'vault', 'amount', 'action_type', 'status', 'invoice', 'created_at')
    list_filter = ('status', 'action_type', 'created_at')
    search_fields = ('vault__representative__username', 'invoice__invoice_no')
    
    # 🆕 إضافة "أكشن" لتوريد النقدية دفعة واحدة
    actions = ['mark_as_settled']

    @admin.action(description="تأكيد استلام النقدية (توريد للخزنة)")
    def mark_as_settled(self, request, queryset):
        # تصفية الحركات المعلقة فقط
        pending_actions = queryset.filter(status='HOLD')
        
        if not pending_actions.exists():
            self.message_user(request, "لا توجد حركات معلقة لتوريدها.", messages.WARNING)
            return

        with transaction.atomic():
            total_collected = 0
            for action in pending_actions:
                # 1. تحديث حالة الحركة
                action.status = 'SETTLED'
                action.settled_at = timezone.now()
                action.save()
                
                # 2. خصم المبلغ من محفظة المندوب
                vault = action.vault
                vault.current_cash_balance -= action.amount
                vault.last_clearance_date = timezone.now()
                vault.save()
                
                total_collected += action.amount

            # 3. إضافة المبلغ للخزينة المركزية
            treasury, _ = CompanyTreasury.objects.get_or_create(name="الخزينة المركزية")
            treasury.total_balance += total_collected
            treasury.save()

        self.message_user(
            request, 
            f"تم توريد مبلغ {total_collected} ج.م إلى الخزينة المركزية بنجاح.", 
            messages.SUCCESS
        )

@admin.register(CompanyTreasury)
class CompanyTreasuryAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_balance')
    readonly_fields = ('total_balance',)

    def has_add_permission(self, request):
        # منع إضافة أكثر من خزينة مركزية واحدة
        return not CompanyTreasury.objects.exists()

