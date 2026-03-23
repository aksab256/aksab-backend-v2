from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم القسم")

    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"

    def __str__(self):
        return self.name

class Product(models.Model):
    # --- التعريف الأساسي ---
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="القسم")
    name = models.CharField(max_length=255, verbose_name="اسم المنتج")
    sku = models.CharField(max_length=50, unique=True, verbose_name="كود الصنف (SKU)")
    barcode = models.CharField(max_length=100, blank=True, null=True, verbose_name="باركود")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="صورة المنتج")

    # --- نظام الوحدات المتداخلة (Packaging) ---
    base_unit = models.CharField(max_length=20, default='قطعة', verbose_name="الوحدة الصغرى (أصغر شيء)")
    sub_unit = models.CharField(max_length=20, blank=True, null=True, verbose_name="الوحدة المتوسطة (مثلاً دستة)")
    main_unit = models.CharField(max_length=20, default='كرتونة', verbose_name="الوحدة الكبرى")
    
    conversion_factor_sub = models.PositiveIntegerField(default=1, verbose_name="كم قطعة في الوحدة المتوسطة؟")
    conversion_factor_main = models.PositiveIntegerField(default=1, verbose_name="كم قطعة في الكرتونة؟")

    # --- المواصفات اللوجستية (للشحن وحساب الأحمال) ---
    weight = models.DecimalField(max_digits=8, decimal_places=3, default=0, verbose_name="الوزن الإجمالي للكرتونة (كجم)")
    length = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="طول الكرتونة (سم)")
    width = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="عرض الكرتونة (سم)")
    height = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="ارتفاع الكرتونة (سم)")

    # --- تنوع الأصناف (Variants) ---
    size = models.CharField(max_length=20, blank=True, null=True, verbose_name="المقاس (مثلاً L, XL أو 42)")
    color = models.CharField(max_length=30, blank=True, null=True, verbose_name="اللون")

    # --- التسعير ---
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر تكلفة الكرتونة")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر بيع الكرتونة (جمهور)")

    is_active = models.BooleanField(default=True, verbose_name="متاح للبيع")
    created_at = models.DateTimeField(auto_now_add=True)

    # --- الدوال الذكية ---
    @property
    def price_per_piece(self):
        if self.conversion_factor_main > 0:
            return round(self.selling_price / self.conversion_factor_main, 2)
        return self.selling_price

    @property
    def cost_per_piece(self):
        if self.conversion_factor_main > 0:
            return round(self.base_price / self.conversion_factor_main, 2)
        return self.base_price

    @property
    def price_per_sub_unit(self):
        if self.conversion_factor_sub > 0:
            return round(self.price_per_piece * self.conversion_factor_sub, 2)
        return 0

    @property
    def volume_m3(self):
        return (self.length * self.width * self.height) / 1000000

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"

    # --- التعديل الجوهري هنا ---
    def __str__(self):
        variant_info = f" - {self.size}" if self.size else ""
        # إضافة الباركود للنص الظاهر ليتمكن السكربت من العثور عليه
        barcode_info = f" | {self.barcode}" if self.barcode else ""
        return f"{self.name}{variant_info}{barcode_info} ({self.sku})"

