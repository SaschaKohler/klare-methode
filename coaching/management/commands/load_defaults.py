from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from coaching.models import VisionBoardTemplate


class Command(BaseCommand):
    help = 'Load default vision board templates'

    def handle(self, *args, **options):
        # Create default templates
        templates = [
            {
                'name': 'Karriere-Vision',
                'description': 'Ein Board für berufliche Ziele und Träume',
                'template_data': {
                    'background': '#f0f9ff',
                    'elements': [
                        {
                            'type': 'text',
                            'content': 'Meine Karriere-Ziele',
                            'x': 50,
                            'y': 50,
                            'width': 300,
                            'height': 100,
                            'color': '#ffffff',
                            'font_size': 24,
                            'text_color': '#1e40af'
                        }
                    ]
                },
                'is_default': True
            },
            {
                'name': 'Persönliche Entwicklung',
                'description': 'Fokussiert auf persönliches Wachstum und Selbstverbesserung',
                'template_data': {
                    'background': '#fef3c7',
                    'elements': [
                        {
                            'type': 'text',
                            'content': 'Persönliches Wachstum',
                            'x': 50,
                            'y': 50,
                            'width': 300,
                            'height': 100,
                            'color': '#ffffff',
                            'font_size': 24,
                            'text_color': '#92400e'
                        }
                    ]
                },
                'is_default': True
            },
            {
                'name': 'Lebensziele',
                'description': 'Umfassende Vision für alle Lebensbereiche',
                'template_data': {
                    'background': '#ecfdf5',
                    'elements': [
                        {
                            'type': 'text',
                            'content': 'Meine Lebensvision',
                            'x': 50,
                            'y': 50,
                            'width': 300,
                            'height': 100,
                            'color': '#ffffff',
                            'font_size': 24,
                            'text_color': '#166534'
                        }
                    ]
                },
                'is_default': True
            }
        ]

        for template_data in templates:
            template, created = VisionBoardTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created template "{template.name}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Template "{template.name}" already exists')
                )