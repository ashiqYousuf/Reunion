from django.urls import path
from . import views


urlpatterns = [
    path('authenticate/' , views.UserLoginView.as_view() , name='authenticate'),
    path('follow/<int:id>/' , views.UserFollowView.as_view() , name='follow'),
    path('unfollow/<int:id>/' , views.UserUnFollowView.as_view() , name='unfollow'),
    path('user/' , views.UserProfileView.as_view() , name='user'),
    path('posts/' , views.CreatePostView.as_view() , name='create-post'),
    path('posts/<int:id>/' , views.RetrieveDeletePostView.as_view() , name='delete-post'),
    path('like/<int:id>/' , views.LikePost.as_view() , name='like'),
    path('unlike/<int:id>/' , views.DislikePost.as_view() , name='dislike'),
    path('comment/<int:id>/' , views.CommentView.as_view() ,name='comment'),
    path('all_posts/' , views.GetAllPosts.as_view() , name='get_all_posts'),
]
