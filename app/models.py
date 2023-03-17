from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import MinLengthValidator



class UserManager(BaseUserManager):
    def create_user(self, email, name , password=None , password2=None):

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):

        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=255 , validators=[MinLengthValidator(4)])
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin


class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    class Meta:
        unique_together = ('user', 'following')

    def save(self, *args, **kwargs):
        # Check if the user has already followed the following user
        try:
            existing_follow = Follower.objects.get(user=self.user, following=self.following)
            # If the follow already exists, delete it
            if existing_follow:
                existing_follow.delete()
        except Follower.DoesNotExist:
            pass

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} Follower'


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    desc = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    
    def __str__(self):
        return f'{self.user.name} commented {self.post.title}'


class Like(models.Model):
    LIKE_CHOICES = (
        (True, 'Like'),
        (False, 'Dislike'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    is_like = models.BooleanField(choices=LIKE_CHOICES, default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post', 'is_like')

    def save(self, *args, **kwargs):
        # If the user is changing their vote, delete the previous vote
        try:
            previous_vote = Like.objects.get(user=self.user, post=self.post)
            if previous_vote.is_like != self.is_like:
                previous_vote.delete()
        except Like.DoesNotExist:
            pass

        super().save(*args, **kwargs)
