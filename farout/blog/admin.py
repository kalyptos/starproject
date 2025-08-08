# blog/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Category, Tag, PostImage

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    fields = ['image', 'caption', 'alt_text', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = 'Post Count'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = 'Post Count'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'created_at', 'published_at', 'views', 'featured_image_preview']
    list_filter = ['status', 'category', 'tags', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['author', 'created_at', 'updated_at', 'published_at', 'views', 'reading_time_display', 'featured_image_preview']
    inlines = [PostImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'status')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Categorization', {
            'fields': ('category', 'tags'),
            'classes': ('collapse',)
        }),
        ('SEO and Media', {
            'fields': ('meta_description', 'featured_image', 'featured_image_preview'),
            'classes': ('collapse',)
        }),
        ('Author and Timestamps', {
            'fields': ('author', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse', 'readonly')
        }),
        ('Statistics', {
            'fields': ('views', 'reading_time_display'),
            'classes': ('collapse',)
        }),
    )
    
    def featured_image_preview(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="150" height="100" style="object-fit: cover;" />', obj.featured_image.url)
        return "No featured image"
    featured_image_preview.short_description = 'Featured Image Preview'
    
    def reading_time_display(self, obj):
        return f"{obj.get_reading_time()} min"
    reading_time_display.short_description = 'Reading Time'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If it's a new object
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Show only posts from logged in user, unless user is superuser"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)