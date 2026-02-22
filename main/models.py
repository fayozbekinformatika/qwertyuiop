from django.db import models, transaction
from django.utils import timezone
from django.utils.text import slugify

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, default='fa-solid fa-book')
    description = models.TextField(default='Kurs haqida qisqacha ma\'lumot')
    level = models.CharField(
        max_length=50,
        choices=[
            ('Boshlang\'ich', 'Boshlang\'ich'),
            ('O\'rta', 'O\'rta'),
            ('Yuqori', 'Yuqori')
        ]
    )
    lesson_count = models.IntegerField(default=0)
    progress = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_progress_for_user(self, user):
        """Foydalanuvchi uchun kurs progressini hisobla"""
        total_lessons = self.lessons.count()
        if total_lessons == 0:
            return 0
        completed = UserProgress.objects.filter(
            user=user, 
            lesson__course=self, 
            completed=True
        ).count()
        return int((completed / total_lessons) * 100)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Update parent course lesson count
        self.course.lesson_count = self.course.lessons.count() + (1 if not self.pk else 0)
        self.course.save(update_fields=['lesson_count'])
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    image = models.CharField(max_length=200, blank=True, default='')
    link = models.CharField(max_length=200, blank=True, default='#')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug =slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    
    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.text[:50]

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text


class BotMessage(models.Model):
    """Test Bot xabarlarini saqlash uchun model"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True, related_name='bot_messages')
    session_id = models.CharField(max_length=100, blank=True, default='')
    user_message = models.TextField(blank=True, default='')
    bot_code = models.TextField(blank=True, default='')
    bot_reply = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Bot Message {self.id} - {self.created_at}"


class UserProgress(models.Model):
    """Foydalanuvchining qaysi darslarni o'qiganini kuzatish"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='completed_by')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'lesson']
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"


class UserProfile(models.Model):
    """Foydalanuvchi profili - PRO va VIP holati"""
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    is_vip = models.BooleanField(default=False)
    vip_since = models.DateTimeField(null=True, blank=True)
    pro_expires = models.DateTimeField(null=True, blank=True)
    vip_emails = models.TextField(blank=True, default='', help_text="VIP foydalanuvchilar ro'yxati, vergul bilan ajratilgan emaillar")
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True, default='')
    banned_at = models.DateTimeField(null=True, blank=True)
    banned_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='banned_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        status = []
        if self.is_vip:
            status.append('VIP')
        if self.is_banned:
            status.append('Banned')
        if not status:
            status.append('Oddiy')
        return f"{self.user.username} - {', '.join(status)}"
    
    def is_pro(self):
        """PRO yoki VIP ekanligini tekshiradi"""
        if self.is_banned:
            return False
        if self.is_vip:
            return True
        if self.pro_expires and self.pro_expires > timezone.now():
            return True
        return False


class PROPayment(models.Model):
    """PRO to'lovlari tarixi"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='pro_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='card')
    transaction_id = models.CharField(max_length=100, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.is_verified}"
