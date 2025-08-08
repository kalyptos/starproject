# blog/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Title')
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name='Author')
    content = models.TextField(verbose_name='Content')
    
    # Categories and tags
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Category')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Tags')
    
    # Automatic timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated')
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='Published')
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='Status')
    
    # SEO and metadata
    meta_description = models.CharField(max_length=160, blank=True, verbose_name='Meta Description')
    featured_image = models.ImageField(upload_to='blog/featured/', blank=True, verbose_name='Featured Image')
    
    # Statistics
    views = models.PositiveIntegerField(default=0, verbose_name='Views')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def get_excerpt(self, length=150):
        """Genererer sammendrag fra innholdet"""
        import re
        # Fjern HTML-tags hvis det finnes
        text = re.sub(r'<[^>]+>', '', self.content)
        if len(text) <= length:
            return text
        return text[:length].rsplit(' ', 1)[0] + '...'
        """Beregner omtrentlig lesetid basert på ordantall"""
        word_count = len(self.content.split())
        reading_time = word_count // 200  # 200 ord per minutt
        return max(1, reading_time)
    
    def get_related_posts(self, limit=3):
        """Henter relaterte innlegg basert på kategori og tags"""
        related = Post.objects.filter(
            status='published'
        ).exclude(id=self.id)
        
        if self.category:
            related = related.filter(category=self.category)
        
        return related[:limit]

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', verbose_name='Post')
    image = models.ImageField(upload_to='blog/gallery/', verbose_name='Image')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Caption')
    alt_text = models.CharField(max_length=100, blank=True, verbose_name='Alt Text')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Uploaded')
    
    class Meta:
        ordering = ['order', 'uploaded_at']
        verbose_name = 'Post Image'
        verbose_name_plural = 'Post Images'
    
    def __str__(self):
        return f"{self.post.title} - Image {self.order}"
    
    def save(self, *args, **kwargs):
        if not self.alt_text:
            self.alt_text = self.caption or f"Image for {self.post.title}"
        super().save(*args, **kwargs)