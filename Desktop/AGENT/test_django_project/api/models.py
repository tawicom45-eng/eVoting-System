from django.db import models


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    age = models.IntegerField()

    def __str__(self):
        return self.name


class Post(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    likes = 0

    def __str__(self):
        return self.title

    def clean(self):
        """Validate model fields."""
        if self.age and not self.age > 0 and self.age < 150:
            raise ValueError(f"Invalid age")
