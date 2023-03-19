from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserLoginSerializer , PostSerializer , CommentSerializer , CommentDetailSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .renderers import CustomRenderer
from rest_framework.permissions import IsAuthenticated , AllowAny
from .models import User , Follower , Post , Comment , Like
from rest_framework.decorators import permission_classes
from django.http import JsonResponse


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserLoginView(APIView):
    renderer_classes = [CustomRenderer]
    def post(self , request , format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email , password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response(
                {
                    'msg': 'Logedin Successfully',
                    'token': token,
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'errors': {'non_field_errors': ['Invalid email or password']}},
                status=status.HTTP_404_NOT_FOUND
            )

class UserFollowView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self , request , id , format=None):
        try:
            following_to = User.objects.get(pk=id)
            Follower(user=following_to , following=request.user).save()
        except:
            return Response({'error': "User you want to follow does'nt exist"} , status=status.HTTP_404_NOT_FOUND)
        return Response({'msg': f'{request.user.name} starts following {following_to.name}'} , status=status.HTTP_200_OK)

class UserUnFollowView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self , request, id , format=None):
        try:
            following_to = User.objects.get(pk=id)
            try:
                Follower.objects.get(user=following_to , following=request.user).delete()
            except:
                return Response({'error': "Already not following this user"} , status=status.HTTP_200_OK)
            return Response({'msg': f'{request.user.name} unfollowed {following_to.name}'})
        except :
            return Response({'error': "User you want to unfollow does'nt exist"} , status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self , request , format=None):
        user = request.user
        username = user.name
        followers = user.followers.count()
        following = user.following.count()
        return Response(
            {
                'username': username,
                'followers': followers,
                'following': following,
            },
            status=status.HTTP_200_OK
        )

class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]
    def post(self , request , format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            print(serializer.data)
            title = serializer.data.get('title')
            desc = serializer.data.get('desc')
            post = Post(user=request.user , title=title , desc=desc)
            post.save()
            return Response(
                {
                    'post_id': post.id,
                    'title': post.title,
                    'description': post.desc,
                    'created_time': post.created_at.isoformat(),
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response({'msg': 'Invalid or Inconsistent Data'} , status=status.HTTP_400_BAD_REQUEST)

class LikePost(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]
    def post(self , request , id , format=None):
        try:
            post = Post.objects.get(pk=id)
            vote = Like(user=request.user , post=post , is_like=True)
            try:
                vote.save()
                return Response({'msg': f"Post Liked"} , status=status.HTTP_201_CREATED)
            except:
                return Response({'error': 'You can not like the post again'} , status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': f'Post with id {id} does not exist'} , status=status.HTTP_404_NOT_FOUND)

class DislikePost(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]
    def post(self , request , id , format=None):
        try:
            post = Post.objects.get(pk=id)
            vote = Like(user=request.user , post=post , is_like=False)
            try:
                vote.save()
                return Response({'msg': f"Post Disliked"} , status=status.HTTP_201_CREATED)
            except:
                return Response({'error': 'You can not dislike the post again'} , status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': f'Post with id {id} does not exist'} , status=status.HTTP_404_NOT_FOUND)



class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]
    # user post content
    def post(self , request , id , format=None):
        post = None
        try:
            post = Post.objects.get(pk=id)
        except:
            return Response({'error': f"Post with id {id} does'nt exist"} , status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        content = serializer.data.get('content')
        comment = Comment(user=request.user , post=post , content=content)
        comment.save()
        return Response({'comment-ID': comment.id} , status=status.HTTP_201_CREATED)


class RetrieveDeletePostView(APIView):
    renderer_classes = [CustomRenderer]

    @permission_classes([IsAuthenticated])
    def delete(self , request , id , format=None):
        post = None
        try:
            post = Post.objects.get(pk=id)
        except:
            return Response({'error': "Post does'nt exist"} , status=status.HTTP_404_NOT_FOUND)
        # Get all posts for the current user
        posts = request.user.posts.all()
        if post in posts:
            post.delete()
            return Response({'msg': 'Post deleted successfully'} ,status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You are not authorized to delete this post'} , status=status.HTTP_400_BAD_REQUEST)
    
    def get(self , request , id , format=None):
        post = None
        try:
            post = Post.objects.get(pk=id)
        except:
            return Response({'error': f"Post with id {id} does'nt exist"} , status=status.HTTP_404_NOT_FOUND)
        likes = post.likes.filter(is_like=True).count()
        comments = post.comments.all()
        serializer = CommentDetailSerializer(comments , many=True)
        return Response(
            {
                'post_id': id,
                'likes': likes,
                'comments': serializer.data,
            },
            status=status.HTTP_200_OK
        )
# - GET /api/all_posts would return all posts created by authenticated user sorted by post time.
#     - RETURN: For each post return the following values
#         - id: ID of the post
#         - title: Title of the post
#         - desc: Description of the post
#         - created_at: Date and time when the post was created
#         - comments: Array of comments, for the particular post
#         - likes: Number of likes for the particular post

class GetAllPosts(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self , request , format=None):
        user = request.user
        post_objs = Post.objects.filter(user=user).order_by('created_at')
        posts = []
        for post in post_objs:
            comments = post.comments.all()
            serializer = CommentDetailSerializer(comments , many=True)
            likes = post.likes.filter(is_like=True).count()
            posts.append(
                {
                    "id": post.id,
                    "title": post.title,
                    "desc": post.desc,
                    "created_at": post.created_at.isoformat(),
                    "likes": likes,
                    "comments": serializer.data,
                }
            )
        return JsonResponse({'posts': posts})
