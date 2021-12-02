from django.db import models


class Category(models.Model):
    title = models.CharField(
        unique=True,
        max_length=150
    )
    
    def __str__(self) -> str:
        return self.title


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        related_name="category_products",
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=150)
    price = models.DecimalField(
        max_digits=9,
        decimal_places=2
    )
    description = models.TextField()
    image_url = models.URLField()
    created_date = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self) -> str:
        return self.title
