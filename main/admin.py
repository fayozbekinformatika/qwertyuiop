from django.contrib import admin
from .models import BlogPost, Course, Lesson, Project, Quiz, Question, Answer, BotMessage, UserProfile, PROPayment

@admin.register(BlogPost)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'icon', 'lesson_count')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    prepopulated_fields = {'slug': ('title',)}

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    list_filter = ('course',)
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'order')
    list_filter = ('quiz',)
    inlines = [AnswerInline]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('question',)
    list_editable = ('is_correct',)


@admin.register(BotMessage)
class BotMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_message', 'bot_code', 'bot_reply', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user_message', 'bot_code', 'bot_reply')
    readonly_fields = ('created_at',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_vip', 'pro_expires', 'is_banned', 'created_at')
    list_filter = ('is_vip', 'is_banned', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_vip', 'is_banned')


@admin.register(PROPayment)
class PROPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'payment_method', 'created_at')
    search_fields = ('user__username', 'transaction_id')
    readonly_fields = ('transaction_id', 'created_at')
