from django.contrib import admin
from .models import Certificate, CertificateTemplate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'final_score', 'issued_date', 'is_verified', 'verification_code')
    list_filter = ('is_verified', 'issued_date', 'course__category')
    search_fields = ('student__username', 'course__title', 'verification_code', 'certificate_id')
    readonly_fields = ('certificate_id', 'issued_date', 'verification_code', 'created_at', 'updated_at')
    ordering = ('-issued_date',)

    fieldsets = (
        ('Certificate Information', {
            'fields': ('certificate_id', 'student', 'course', 'enrollment')
        }),
        ('Completion Details', {
            'fields': ('completion_date', 'final_score', 'issued_date')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_code')
        }),
        ('Files', {
            'fields': ('pdf_file',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'is_default', 'created_at')
    list_filter = ('is_active', 'is_default', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Colors', {
            'fields': ('background_color', 'text_color', 'border_color')
        }),
        ('Images', {
            'fields': ('logo', 'background_image')
        }),
        ('Typography', {
            'fields': ('title_font_size', 'body_font_size')
        }),
        ('Status', {
            'fields': ('is_active', 'is_default')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
