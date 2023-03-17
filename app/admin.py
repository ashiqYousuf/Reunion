from django.contrib import admin
from .models import User , Follower , Post , Comment , Like
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):

    list_display = ('id' , 'email', 'name', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id' , 'user' , 'title']

@admin.register(Like)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id' , 'user' , 'post' , 'is_like']

admin.site.register(Follower)
admin.site.register(Comment)
