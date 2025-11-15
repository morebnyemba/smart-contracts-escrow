from django.core.management.base import BaseCommand
from django.utils.text import slugify
from users.models import ServiceCategory


class Command(BaseCommand):
    help = 'Create initial service categories'

    def handle(self, *args, **options):
        categories = [
            'Web Development',
            'Mobile Development',
            'Graphic Design',
            'Content Writing',
            'Digital Marketing',
            'Video Editing',
            'Data Analysis',
            'Virtual Assistant',
            'Legal Services',
            'Consulting',
        ]

        for category_name in categories:
            category, created = ServiceCategory.objects.get_or_create(
                name=category_name,
                defaults={'slug': slugify(category_name)}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category_name}')
                )
