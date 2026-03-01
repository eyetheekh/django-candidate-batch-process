import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.core.models import User, UserRole
from apps.candidates.models import Candidate, CandidateStatus

class Command(BaseCommand):
    help = "Seed the database with dummy users and a large number of candidates"

    def add_arguments(self, parser):
        parser.add_argument(
            '--candidates',
            type=int,
            default=1000,
            help='Number of random candidates to generate (default: 1000)'
        )

    def handle(self, *args, **options):
        num_candidates = options['candidates']
        fake = Faker()

        self.stdout.write(self.style.WARNING("Starting database seed..."))

        # Admin User
        admin_email = 'admin@dj.dj'
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                password=admin_email,
            )
            self.stdout.write(self.style.SUCCESS(f'Created Admin User: {admin_email} / {admin_email}'))
        else:
            self.stdout.write(f'Admin user ({admin_email}) already exists.')

        # Reviewer User
        reviewer_email = 'reviewer1@dj.dj'
        if not User.objects.filter(email=reviewer_email).exists():
            # The custom user manager exposes create_user
            User.objects.create_user(
                email=reviewer_email,
                password=reviewer_email,
                role=UserRole.REVIEWER
            )
            self.stdout.write(self.style.SUCCESS(f'Created Reviewer User: {reviewer_email} / {reviewer_email}'))
        else:
            self.stdout.write(f'Reviewer user ({reviewer_email}) already exists.')

        # Candidates Generation
        self.stdout.write(f"Generating {num_candidates} Candidates (this may take a few moments)...")

        candidates_to_create = []
        statuses = [
            CandidateStatus.PENDING, 
            CandidateStatus.PROCESSING, 
            CandidateStatus.SUCCESS, 
            CandidateStatus.FAILED
        ]
        
        #unique emails
        # Also need to reset Faker's unique set to avoid constraint errors across consecutive runs
        fake.unique.clear()

        for _ in range(num_candidates):
            status = random.choices(statuses, weights=[65, 5, 20, 10], k=1)[0]
            
            # Setup phone string properly sliced to fit DB max_length=20
            raw_phone = fake.phone_number()
            phone = raw_phone[:20] if len(raw_phone) > 20 else raw_phone

            # Initialize mock attempt variables based on selected state
            attempt_count = random.randint(1, 4) if status in [CandidateStatus.FAILED, CandidateStatus.SUCCESS] else 0
            
            c = Candidate(
                name=fake.name(),
                email=fake.unique.email(),
                phone_number=phone,
                link=fake.url() if random.random() > 0.2 else None,  # 80% have links
                dob=fake.date_of_birth(minimum_age=18, maximum_age=60),
                status=status,
                attempt_count=attempt_count,
            )

            if status in [CandidateStatus.FAILED, CandidateStatus.SUCCESS] or status == CandidateStatus.PROCESSING:
                c.last_attempt_at = timezone.now() - timezone.timedelta(hours=random.randint(1, 48))

            if status == CandidateStatus.PROCESSING:
                c.picked_at = timezone.now()

            candidates_to_create.append(c)

        # Bulk insert to hit SQLite as gracefully/quickly as possible
        Candidate.objects.bulk_create(candidates_to_create, batch_size=500)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully injected {num_candidates} random candidates.'))

