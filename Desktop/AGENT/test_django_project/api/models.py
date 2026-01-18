from django.db import models


class User(models.Model):
    """Class: function"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    age = models.IntegerField()

    def __str__(self):
        """Function: function"""
        return self.name


class Post(models.Model):
    """Class: function"""
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    likes = 0

    def __str__(self):
        """Function: function"""
        return self.title
