from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Department, CustomUser
from thesis.models import ResearchWork
import random

class Command(BaseCommand):
    help = 'Populate demo data for users and research works'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting demo data population...')

        # 1. Create Departments
        departments_data = [
            {'name': 'CSE', 'full_name': 'Computer Science and Engineering'},
            {'name': 'EEE', 'full_name': 'Electrical and Electronic Engineering'},
            {'name': 'PHY', 'full_name': 'Physics'},
            {'name': 'CHE', 'full_name': 'Chemistry'},
            {'name': 'MAT', 'full_name': 'Mathematics'},
            {'name': 'BNG', 'full_name': 'Bangla'},
            {'name': 'ENG', 'full_name': 'English'},
            {'name': 'SOC', 'full_name': 'Sociology'},
            {'name': 'ECO', 'full_name': 'Economics'},
            {'name': 'PAD', 'full_name': 'Public Administration'},
        ]
        
        departments = []
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'], 
                defaults={'full_name': dept_data['full_name']}
            )
            if created:
                self.stdout.write(f"Created Department: {dept.name}")
            departments.append(dept)
        
        # 2. Create Users
        User = get_user_model()
        first_names = ['John', 'Jane', 'Alice', 'Bob', 'Charlie', 'Diana', 'Evan', 'Fiona', 'George', 'Hannah', 'Ian', 'Julia', 'Kevin', 'Laura', 'Mike', 'Nina', 'Oscar', 'Paula', 'Quinn', 'Rachel', 'Steve', 'Tina', 'Umar', 'Vera', 'Will', 'Xena', 'Yara', 'Zach']
        last_names = ['Smith', 'Doe', 'Johnson', 'Brown', 'Williams', 'Jones', 'Miller', 'Davis', 'Garcia', 'Rodriguez', 'Wilson', 'Martinez', 'Anderson', 'Taylor', 'Thomas', 'Hernandez', 'Moore', 'Martin', 'Jackson', 'Thompson', 'White', 'Lopez', 'Lee', 'Gonzalez', 'Harris', 'Clark', 'Lewis', 'Robinson', 'Walker', 'Perez']
        
        users_created = 0
        users = []
        
        # Ensure at least 50 users exist
        target_users = 50
        current_users = User.objects.count()
        needed_users = max(0, target_users - current_users)
        
        sessions = [x[0] for x in CustomUser.SESSION_CHOICES]
        blood_groups = [x[0] for x in CustomUser.BLOOD_GROUP_CHOICES]
        genders = [x[0] for x in CustomUser.GENDER_CHOICES]

        # Fetch existing users first
        users.extend(list(User.objects.all()))

        for i in range(needed_users):
            username = f'student_demo_{current_users + i + 1}'
            if not User.objects.filter(username=username).exists():
                first = random.choice(first_names)
                last = random.choice(last_names)
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@sustaura.edu',
                    password='password123',
                    first_name=first,
                    last_name=last,
                    department=random.choice(departments),
                    session=random.choice(sessions) if sessions else '2023-2024',
                    gender=random.choice(genders) if genders else 'O',
                    blood=random.choice(blood_groups) if blood_groups else 'O+',
                    email_verified=True
                )
                users.append(user)
                users_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {users_created} new users. Total users available: {len(users)}'))
        
        # 3. Create Research Works
        titles_adj = ['Advanced', 'Novel', 'Comparative', 'Deep', 'Efficient', 'Dynamic', 'Sustainable', 'Secure', 'Optimized', 'Automated', 'Intelligent', 'Scalable', 'Robust']
        titles_noun = ['Analysis', 'Study', 'Framework', 'Architecture', 'System', 'Algorithm', 'Network', 'Model', 'Approach', 'Platform', 'Methodology', 'Technique']
        titles_topic = ['Cloud Computing', 'IoT', 'Blockchain', 'AI', 'Machine Learning', 'Big Data', 'Cybersecurity', 'Smart Grid', 'Renewable Energy', 'Quantum Computing', 'Data Mining', 'Neural Networks', 'Bioinformatics', 'Robotics']
        
        abstract_start = ['This paper proposes', 'We present a study on', 'An investigation into', 'A novel framework for', 'This research explores', 'The implementation of']
        abstract_mid = ['which significantly improves', 'focusing on the impact of', 'addressing the challenges of', 'utilizing advanced techniques in', 'comparing different approaches to', 'enhancing the performance of']
        abstract_end = ['results showing promise.', 'demonstrating high efficiency.', 'providing a scalable solution.', 'contributing to the field.', 'with future scope identified.', 'validating the proposed model.']
        
        supervisors = ['Dr. Alice Wonderland', 'Prof. Bob Builder', 'Dr. Charlie Chaplin', 'Prof. David Copperfield', 'Dr. Eve Adams', 'Prof. Frank Castle', 'Dr. Grace Hopper', 'Prof. Alan Turing']

        work_types = [x[0] for x in ResearchWork.WORK_TYPES]

        created_works = 0
        target_works = 100
        existing_works = ResearchWork.objects.count()
        needed_works = max(0, target_works - existing_works)

        self.stdout.write(f'Existing works: {existing_works}. Creating {needed_works} more...')

        for _ in range(needed_works):
            title = f"{random.choice(titles_adj)} {random.choice(titles_noun)} of {random.choice(titles_topic)} in {random.choice(titles_topic)}"
            abstract = f"{random.choice(abstract_start)} {random.choice(titles_topic)} {random.choice(abstract_mid)} {random.choice(titles_noun)}, {random.choice(abstract_end)} Furthermore, {random.choice(abstract_start).lower()} generated data to validate the claims."
            
            work_type = random.choice(work_types)
            
            work = ResearchWork.objects.create(
                title=title,
                abstract=abstract,
                supervisor_name=random.choice(supervisors),
                work_type=work_type,
                link='https://example.com/thesis.pdf',
                is_public=True
            )
            
            # Assign 1-3 authors
            if users:
                work_authors = random.sample(users, k=min(len(users), random.randint(1, 3)))
                work.authors.set(work_authors)
            
            created_works += 1
            
        self.stdout.write(self.style.SUCCESS(f'Done! Created {created_works} Research Works. Total in DB: {ResearchWork.objects.count()}'))
