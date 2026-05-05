from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from assessments.models import Answer, Assessment, Choice, Question, Submission
from content.models import LinkContent, TextContent, Title, Topic, Unit
from main.models import Notification
from nests.models import Nest, NestMembership
from posts.models import (
    Comment,
    Post,
    PostReadStatus,
    PostSubscription,
    PostTag,
    PostType,
    PostVote,
)
from recognition.models import NestRecognition


class Command(BaseCommand):
    help = "Seed light but effective demo data with old/new timelines."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Clear existing demo-related data before seeding.",
        )

    @staticmethod
    def _set_dt(obj, field, dt):
        obj.__class__.objects.filter(pk=obj.pk).update(**{field: dt})

    def _reset_data(self):
        User = get_user_model()

        # Delete app data in a safe order while preserving superusers.
        Notification.objects.all().delete()

        Answer.objects.all().delete()
        Submission.objects.all().delete()
        Choice.objects.all().delete()
        Question.objects.all().delete()
        Assessment.objects.all().delete()

        LinkContent.objects.all().delete()
        TextContent.objects.all().delete()
        Topic.objects.all().delete()
        Unit.objects.all().delete()
        Title.objects.all().delete()

        Comment.objects.all().delete()
        PostVote.objects.all().delete()
        PostReadStatus.objects.all().delete()
        PostSubscription.objects.all().delete()
        Post.objects.all().delete()
        PostTag.objects.all().delete()
        PostType.objects.all().delete()

        NestRecognition.objects.all().delete()
        NestMembership.objects.all().delete()
        Nest.objects.all().delete()

        User.objects.filter(is_superuser=False).delete()

    def handle(self, *args, **options):
        now = timezone.now()

        with transaction.atomic():
            if options["reset"]:
                self._reset_data()
                self.stdout.write(self.style.WARNING("Existing demo data reset complete."))

            User = get_user_model()
            admin_user, created = User.objects.get_or_create(
                username="admin",
                defaults={
                    "first_name": "Admin",
                    "last_name": "User",
                    "email": "admin@devnest.demo",
                    "is_staff": True,
                    "is_superuser": True,
                },
            )
            if created:
                admin_user.set_password("DemoPass123!")
                admin_user.save(update_fields=["password"])

            # --- Users ---
            users_data = [
                ("instructor_ali", "Ali", "Hassan", "ali@devnest.demo", False, False),
                ("assistant_noor", "Noor", "Saad", "noor@devnest.demo", False, False),
                ("student_omar", "Omar", "Khalid", "omar@devnest.demo", False, False),
                ("student_sara", "Sara", "Fahad", "sara@devnest.demo", False, False),
                ("student_lina", "Lina", "Saif", "lina@devnest.demo", False, False),
                ("student_hamad", "Hamad", "Nasser", "hamad@devnest.demo", False, False),
                ("site_staff", "Site", "Staff", "staff@devnest.demo", True, False),
            ]

            users = {}
            for username, first_name, last_name, email, is_staff, is_superuser in users_data:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "is_staff": is_staff,
                        "is_superuser": is_superuser,
                    },
                )
                if created:
                    user.set_password("DemoPass123!")
                    user.save(update_fields=["password"])
                users[username] = user
            users[admin_user.username] = admin_user

            # --- Nests ---
            nest_python, _ = Nest.objects.get_or_create(
                name="CS101 - Python Foundations",
                defaults={
                    "description": "Core Python, loops, functions, and practical exercises.",
                    "creator": users["instructor_ali"],
                    "status": Nest.Status.APPROVED,
                },
            )
            nest_ds, _ = Nest.objects.get_or_create(
                name="Data Structures Bootcamp",
                defaults={
                    "description": "Arrays, linked lists, trees, and complexity practice.",
                    "creator": users["instructor_ali"],
                    "status": Nest.Status.APPROVED,
                },
            )
            nest_public, _ = Nest.objects.get_or_create(
                name="Public Nest",
                defaults={
                    "description": "Open community nest for every new user to explore DevNest right away.",
                    "creator": admin_user,
                    "status": Nest.Status.APPROVED,
                },
            )
            nest_pending, _ = Nest.objects.get_or_create(
                name="AI Fundamentals (Summer)",
                defaults={
                    "description": "Proposed nest for summer intro to AI and ML basics.",
                    "creator": users["student_sara"],
                    "status": Nest.Status.PENDING,
                },
            )

            self._set_dt(nest_python, "created_at", now - timedelta(days=95))
            self._set_dt(nest_ds, "created_at", now - timedelta(days=38))
            self._set_dt(nest_public, "created_at", now - timedelta(days=120))
            self._set_dt(nest_pending, "created_at", now - timedelta(days=2))

            memberships = [
                (nest_public, "admin", NestMembership.Role.INSTRUCTOR, NestMembership.Status.ACTIVE, 120),
                (nest_public, "site_staff", NestMembership.Role.ASSISTANT, NestMembership.Status.ACTIVE, 75),
                (nest_public, "student_omar", NestMembership.Role.MEMBER, NestMembership.Status.ACTIVE, 68),
                (nest_public, "student_sara", NestMembership.Role.MEMBER, NestMembership.Status.ACTIVE, 54),
                (nest_public, "student_lina", NestMembership.Role.MEMBER, NestMembership.Status.ACTIVE, 18),
                (nest_public, "student_hamad", NestMembership.Role.MEMBER, NestMembership.Status.ACTIVE, 13),

                (nest_python, "instructor_ali", NestMembership.Role.INSTRUCTOR, NestMembership.Status.ACTIVE, 94),
                (nest_python, "assistant_noor", NestMembership.Role.ASSISTANT, NestMembership.Status.ACTIVE, 80),
                (nest_python, "student_omar", NestMembership.Role.MEMBER, NestMembership.Status.ACTIVE, 60),
                (nest_python, "student_sara", NestMembership.Role.MEMBER, NestMembership.Status.ACTIVE, 40),
                (nest_python, "student_lina", NestMembership.Role.MEMBER, NestMembership.Status.PENDING, 1),

                (nest_ds, "instructor_ali", NestMembership.Role.INSTRUCTOR, NestMembership.Status.ACTIVE, 37),
                (nest_ds, "assistant_noor", NestMembership.Role.ASSISTANT, NestMembership.Status.ACTIVE, 32),
                (nest_ds, "student_hamad", NestMembership.Role.MEMBER, NestMembership.Status.ACTIVE, 21),
                (nest_ds, "student_omar", NestMembership.Role.MEMBER, NestMembership.Status.ACTIVE, 15),
            ]

            for nest, username, role, status, days_ago in memberships:
                membership, _ = NestMembership.objects.get_or_create(
                    nest=nest,
                    user=users[username],
                    defaults={"role": role, "status": status},
                )
                membership.role = role
                membership.status = status
                membership.save(update_fields=["role", "status"])
                self._set_dt(membership, "joined_at", now - timedelta(days=days_ago))

            # --- Post types & tags ---
            pt_question, _ = PostType.objects.get_or_create(name="Question")
            pt_discussion, _ = PostType.objects.get_or_create(name="Discussion")
            pt_announcement, _ = PostType.objects.get_or_create(name="Announcement")

            tags = {}
            for tag_name in ["python", "loops", "functions", "exam-prep", "arrays", "trees", "welcome", "showcase", "community"]:
                tag, _ = PostTag.objects.get_or_create(name=tag_name)
                tags[tag_name] = tag

            # --- Posts (old -> new spread) ---
            posts = []
            posts_data = [
                (nest_python, "instructor_ali", "Welcome to CS101", "Course roadmap and weekly structure.", pt_announcement, True, 90, ["exam-prep"]),
                (nest_python, "student_omar", "When should I use while vs for?", "I get confused choosing loops in practice problems.", pt_question, False, 28, ["python", "loops"]),
                (nest_python, "assistant_noor", "Function naming best practices", "Share naming patterns you use in assignments.", pt_discussion, False, 9, ["python", "functions"]),
                (nest_python, "student_sara", "Mock exam tips for week 8", "Can we share a checklist for debugging under time pressure?", pt_discussion, False, 2, ["exam-prep"]),
                (nest_python, "instructor_ali", "Lab moved to Thursday", "This week only: lab session moved due to campus event.", pt_announcement, True, 0, ["exam-prep"]),

                (nest_ds, "instructor_ali", "Bootcamp kickoff", "Start with arrays and two-pointer techniques.", pt_announcement, True, 35, ["arrays"]),
                (nest_ds, "student_hamad", "Tree traversal cheat sheet", "Posting my DFS/BFS summary. Feedback welcome.", pt_discussion, False, 6, ["trees"]),
                (nest_ds, "student_omar", "Big-O in nested loops", "Need intuition for O(n^2) vs O(n log n).", pt_question, False, 1, ["arrays", "exam-prep"]),
            ]

            for nest, username, title, content, post_type, pinned, days_ago, tag_names in posts_data:
                post, _ = Post.objects.get_or_create(
                    nest=nest,
                    user=users[username],
                    title=title,
                    defaults={"content": content, "post_type": post_type, "is_pinned": pinned},
                )
                post.content = content
                post.post_type = post_type
                post.is_pinned = pinned
                post.save(update_fields=["content", "post_type", "is_pinned"])
                post.tags.set([tags[name] for name in tag_names])

                ts = now - timedelta(days=days_ago, hours=(days_ago % 5) + 2)
                if days_ago == 0:
                    ts = now - timedelta(hours=3)
                self._set_dt(post, "created_at", ts)
                posts.append(post)

            public_posts = []
            public_posts_data = [
                ("admin", "Welcome to the Public Nest", "Start here to explore DevNest. This nest is open to every newly registered user and is meant to showcase the platform.", pt_announcement, True, 118, ["welcome", "community"]),
                ("site_staff", "How to explore the demo", "Check posts first, then open content and assessments to see how a full learning community is organized.", pt_discussion, True, 24, ["showcase", "community"]),
                ("student_lina", "What should I click first?", "I just joined DevNest. What is the fastest way to understand how everything fits together?", pt_question, False, 4, ["welcome", "showcase"]),
                ("student_hamad", "My favorite part of the demo", "The mix of community posts, learning materials, and quick assessments makes the project feel complete.", pt_discussion, False, 1, ["community"]),
            ]
            for username, title, content, post_type, pinned, days_ago, tag_names in public_posts_data:
                post, _ = Post.objects.get_or_create(
                    nest=nest_public,
                    user=users[username],
                    title=title,
                    defaults={"content": content, "post_type": post_type, "is_pinned": pinned},
                )
                post.content = content
                post.post_type = post_type
                post.is_pinned = pinned
                post.save(update_fields=["content", "post_type", "is_pinned"])
                post.tags.set([tags[name] for name in tag_names])

                ts = now - timedelta(days=days_ago, hours=(days_ago % 4) + 1)
                self._set_dt(post, "created_at", ts)
                public_posts.append(post)

            # --- Comments and replies ---
            comments_data = [
                (posts[1], "assistant_noor", "Use `for` when you know iteration bounds; `while` for condition-driven loops.", None, 27),
                (posts[1], "student_sara", "Try both on a small input and inspect variable changes.", None, 26),
                (posts[2], "student_omar", "I prefer verb_noun style like `calculate_score`.", None, 8),
                (posts[3], "instructor_ali", "Great topic. I will post a sample rubric tonight.", None, 1),
                (posts[6], "assistant_noor", "Nice summary. Add preorder/inorder examples.", None, 5),
                (posts[7], "instructor_ali", "We will practice this in tomorrow's session.", None, 0),
            ]

            created_comments = []
            for post, username, content, parent, days_ago in comments_data:
                comment, _ = Comment.objects.get_or_create(
                    post=post,
                    user=users[username],
                    content=content,
                    parent=parent,
                    defaults={"approved": True, "is_verified": False},
                )
                comment.approved = True
                comment.is_verified = users[username] == users["instructor_ali"]
                comment.save(update_fields=["approved", "is_verified"])
                self._set_dt(comment, "created_at", now - timedelta(days=days_ago, hours=1))
                created_comments.append(comment)

            # Add one reply chain for demo
            reply, _ = Comment.objects.get_or_create(
                post=posts[1],
                user=users["student_omar"],
                parent=created_comments[0],
                content="That distinction makes sense now, thanks!",
                defaults={"approved": True, "is_verified": False},
            )
            self._set_dt(reply, "created_at", now - timedelta(days=26, hours=6))

            public_comment_1, _ = Comment.objects.get_or_create(
                post=public_posts[2],
                user=users["admin"],
                content="Start with the pinned post, then open the content library and the sample check-in assessment.",
                parent=None,
                defaults={"approved": True, "is_verified": True},
            )
            public_comment_1.approved = True
            public_comment_1.is_verified = True
            public_comment_1.save(update_fields=["approved", "is_verified"])
            self._set_dt(public_comment_1, "created_at", now - timedelta(days=3, hours=5))

            public_comment_2, _ = Comment.objects.get_or_create(
                post=public_posts[2],
                user=users["student_sara"],
                content="I would browse the posts tab first because it quickly shows announcements, questions, and community activity.",
                parent=None,
                defaults={"approved": True, "is_verified": False},
            )
            public_comment_2.approved = True
            public_comment_2.is_verified = False
            public_comment_2.save(update_fields=["approved", "is_verified"])
            self._set_dt(public_comment_2, "created_at", now - timedelta(days=2, hours=8))

            public_reply, _ = Comment.objects.get_or_create(
                post=public_posts[2],
                user=users["student_lina"],
                parent=public_comment_1,
                content="Perfect, that gives me a starting path.",
                defaults={"approved": True, "is_verified": False},
            )
            self._set_dt(public_reply, "created_at", now - timedelta(days=2, hours=4))

            # --- Votes ---
            votes_data = [
                (posts[1], "assistant_noor", 1),
                (posts[1], "student_sara", 1),
                (posts[2], "student_omar", 1),
                (posts[2], "student_sara", 1),
                (posts[6], "instructor_ali", 1),
                (posts[7], "assistant_noor", 1),
                (posts[7], "student_hamad", 1),
            ]
            for post, username, value in votes_data:
                vote, _ = PostVote.objects.get_or_create(post=post, user=users[username], defaults={"value": value})
                vote.value = value
                vote.save(update_fields=["value"])

            public_votes_data = [
                (public_posts[2], "admin", 1),
                (public_posts[2], "student_sara", 1),
                (public_posts[3], "student_omar", 1),
                (public_posts[3], "student_lina", 1),
            ]
            for post, username, value in public_votes_data:
                vote, _ = PostVote.objects.get_or_create(post=post, user=users[username], defaults={"value": value})
                vote.value = value
                vote.save(update_fields=["value"])

            # --- Subscriptions / read status ---
            for post in posts:
                for username in ["student_omar", "student_sara", "student_hamad"]:
                    if post.nest == nest_python and username == "student_hamad":
                        continue
                    sub, _ = PostSubscription.objects.get_or_create(post=post, user=users[username])
                    sub.is_enabled = True
                    sub.save(update_fields=["is_enabled"])

            for post in public_posts:
                for username in ["student_omar", "student_sara", "student_hamad", "student_lina"]:
                    sub, _ = PostSubscription.objects.get_or_create(post=post, user=users[username])
                    sub.is_enabled = True
                    sub.save(update_fields=["is_enabled"])

            # Mark old posts as read for one student; keep newer ones unread for demo
            for post in posts:
                if (now - post.created_at).days >= 7:
                    rs, _ = PostReadStatus.objects.get_or_create(post=post, user=users["student_omar"])
                    self._set_dt(rs, "read_at", now - timedelta(days=1))

            # --- Assessments ---
            quiz, _ = Assessment.objects.get_or_create(
                nest=nest_python,
                title="Quiz 1 - Python Basics",
                defaults={
                    "description": "Variables, loops, and functions.",
                    "assessment_type": "quiz",
                    "points": 20,
                    "due_date": now - timedelta(days=14),
                    "created_by": users["instructor_ali"],
                },
            )
            self._set_dt(quiz, "created_at", now - timedelta(days=30))

            assignment, _ = Assessment.objects.get_or_create(
                nest=nest_python,
                title="Assignment 2 - Practice Set",
                defaults={
                    "description": "Solve 5 short coding tasks with explanation.",
                    "assessment_type": "assignment",
                    "points": 40,
                    "due_date": now + timedelta(days=5),
                    "created_by": users["assistant_noor"],
                },
            )
            self._set_dt(assignment, "created_at", now - timedelta(days=3))

            q1, _ = Question.objects.get_or_create(
                assessment=quiz,
                text="Which loop is best when the number of iterations is known?",
                defaults={"question_type": "mcq", "points": 5},
            )
            q2, _ = Question.objects.get_or_create(
                assessment=quiz,
                text="Explain why functions improve maintainability.",
                defaults={"question_type": "text", "points": 5},
            )
            c1, _ = Choice.objects.get_or_create(question=q1, text="for loop", defaults={"is_correct": True})
            Choice.objects.get_or_create(question=q1, text="while loop", defaults={"is_correct": False})

            sub_omar, _ = Submission.objects.get_or_create(assessment=quiz, student=users["student_omar"], defaults={"score": 8})
            self._set_dt(sub_omar, "submitted_at", now - timedelta(days=13))
            Answer.objects.get_or_create(submission=sub_omar, question=q1, defaults={"selected_choice": c1, "is_correct": True})
            Answer.objects.get_or_create(submission=sub_omar, question=q2, defaults={"text_answer": "Functions remove duplication.", "is_correct": True})

            public_quiz, _ = Assessment.objects.get_or_create(
                nest=nest_public,
                title="Public Nest Check-in",
                defaults={
                    "description": "Quick orientation quiz for visitors exploring the demo nest.",
                    "assessment_type": "quiz",
                    "points": 10,
                    "due_date": now + timedelta(days=10),
                    "created_by": admin_user,
                },
            )
            self._set_dt(public_quiz, "created_at", now - timedelta(days=15))

            public_q1, _ = Question.objects.get_or_create(
                assessment=public_quiz,
                text="Which nest is open to every newly registered user?",
                defaults={"question_type": "mcq", "points": 5},
            )
            public_q2, _ = Question.objects.get_or_create(
                assessment=public_quiz,
                text="Name one area you can explore from Public Nest.",
                defaults={"question_type": "text", "points": 5},
            )
            public_c1, _ = Choice.objects.get_or_create(question=public_q1, text="Public Nest", defaults={"is_correct": True})
            Choice.objects.get_or_create(question=public_q1, text="Pending Requests", defaults={"is_correct": False})

            sub_public, _ = Submission.objects.get_or_create(assessment=public_quiz, student=users["student_lina"], defaults={"score": 10})
            self._set_dt(sub_public, "submitted_at", now - timedelta(days=1))
            Answer.objects.get_or_create(submission=sub_public, question=public_q1, defaults={"selected_choice": public_c1, "is_correct": True})
            Answer.objects.get_or_create(submission=sub_public, question=public_q2, defaults={"text_answer": "Posts, content, and the sample assessment.", "is_correct": True})

            # --- Content ---
            title_public, _ = Title.objects.get_or_create(
                nest=nest_public,
                created_by=admin_user,
                name="Start Here - DevNest Tour",
                defaults={"description": "Orientation materials for first-time visitors.", "sort_order": 1, "is_published": True},
            )
            self._set_dt(title_public, "created_at", now - timedelta(days=60))

            unit_public, _ = Unit.objects.get_or_create(
                title=title_public,
                name="Getting Started",
                defaults={"description": "A short walkthrough of the demo space.", "sort_order": 1, "is_published": True},
            )
            self._set_dt(unit_public, "created_at", now - timedelta(days=59))

            topic_public, _ = Topic.objects.get_or_create(
                unit=unit_public,
                name="Explore the Demo",
                defaults={"sort_order": 1, "status": Topic.StatusChoices.PUBLISHED, "due_date": now + timedelta(days=14)},
            )
            self._set_dt(topic_public, "created_at", now - timedelta(days=58))

            TextContent.objects.get_or_create(
                topic=topic_public,
                text_title="Where to click first",
                defaults={"body": "Open posts for community activity, then visit content and assessments to see a full learning workflow.", "format": "plain", "sort_order": 1},
            )
            LinkContent.objects.get_or_create(
                topic=topic_public,
                display_text="Django official tutorial",
                defaults={"url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/", "sort_order": 2},
            )

            title_py, _ = Title.objects.get_or_create(
                nest=nest_python,
                created_by=users["instructor_ali"],
                name="Week 1 - Python Essentials",
                defaults={"description": "Starter materials for week 1", "sort_order": 1, "is_published": True},
            )
            self._set_dt(title_py, "created_at", now - timedelta(days=32))

            unit_intro, _ = Unit.objects.get_or_create(
                title=title_py,
                name="Intro Unit",
                defaults={"description": "Getting started", "sort_order": 1, "is_published": True},
            )
            self._set_dt(unit_intro, "created_at", now - timedelta(days=31))

            topic_loops, _ = Topic.objects.get_or_create(
                unit=unit_intro,
                name="Loops and Control Flow",
                defaults={"sort_order": 1, "status": Topic.StatusChoices.PUBLISHED, "due_date": now - timedelta(days=20)},
            )
            self._set_dt(topic_loops, "created_at", now - timedelta(days=30))

            topic_functions, _ = Topic.objects.get_or_create(
                unit=unit_intro,
                name="Functions Deep Dive",
                defaults={"sort_order": 2, "status": Topic.StatusChoices.PUBLISHED, "due_date": now + timedelta(days=2)},
            )
            self._set_dt(topic_functions, "created_at", now - timedelta(days=4))

            TextContent.objects.get_or_create(
                topic=topic_loops,
                text_title="Loop Patterns Summary",
                defaults={"body": "Use for for bounded loops and while for condition-driven loops.", "format": "plain", "sort_order": 1},
            )
            LinkContent.objects.get_or_create(
                topic=topic_functions,
                display_text="Official Python docs: Defining Functions",
                defaults={"url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions", "sort_order": 1},
            )

            # --- DS Nest content ---
            title_ds, _ = Title.objects.get_or_create(
                nest=nest_ds,
                created_by=users["instructor_ali"],
                name="Week 1 - Arrays & Complexity",
                defaults={"description": "Foundation concepts for data structures.", "sort_order": 1, "is_published": True},
            )
            self._set_dt(title_ds, "created_at", now - timedelta(days=36))

            unit_arrays, _ = Unit.objects.get_or_create(
                title=title_ds,
                name="Arrays & Two-Pointer",
                defaults={"description": "Core array techniques.", "sort_order": 1, "is_published": True},
            )
            self._set_dt(unit_arrays, "created_at", now - timedelta(days=35))

            topic_complexity, _ = Topic.objects.get_or_create(
                unit=unit_arrays,
                name="Big-O Complexity",
                defaults={"sort_order": 1, "status": Topic.StatusChoices.PUBLISHED, "due_date": now - timedelta(days=10)},
            )
            self._set_dt(topic_complexity, "created_at", now - timedelta(days=34))

            topic_twopointer, _ = Topic.objects.get_or_create(
                unit=unit_arrays,
                name="Two-Pointer Technique",
                defaults={"sort_order": 2, "status": Topic.StatusChoices.PUBLISHED, "due_date": now + timedelta(days=4)},
            )
            self._set_dt(topic_twopointer, "created_at", now - timedelta(days=20))

            TextContent.objects.get_or_create(
                topic=topic_complexity,
                text_title="Big-O Quick Reference",
                defaults={"body": "O(1) constant, O(log n) binary search, O(n) linear scan, O(n log n) merge sort, O(n^2) nested loops.", "format": "plain", "sort_order": 1},
            )
            LinkContent.objects.get_or_create(
                topic=topic_twopointer,
                display_text="Two Pointers - LeetCode Patterns",
                defaults={"url": "https://leetcode.com/tag/two-pointers/", "sort_order": 1},
            )
            TextContent.objects.get_or_create(
                topic=topic_twopointer,
                text_title="Two-Pointer Template",
                defaults={"body": "left, right = 0, len(arr)-1\nwhile left < right:\n    # process\n    left += 1 or right -= 1", "format": "plain", "sort_order": 2},
            )

            # --- CS101 Week 2 content ---
            title_py2, _ = Title.objects.get_or_create(
                nest=nest_python,
                created_by=users["instructor_ali"],
                name="Week 2 - Data & Files",
                defaults={"description": "Lists, dicts, file I/O and error handling.", "sort_order": 2, "is_published": True},
            )
            self._set_dt(title_py2, "created_at", now - timedelta(days=18))

            unit_data, _ = Unit.objects.get_or_create(
                title=title_py2,
                name="Collections",
                defaults={"description": "Lists, tuples, and dicts.", "sort_order": 1, "is_published": True},
            )
            self._set_dt(unit_data, "created_at", now - timedelta(days=17))

            topic_lists, _ = Topic.objects.get_or_create(
                unit=unit_data,
                name="Lists and Comprehensions",
                defaults={"sort_order": 1, "status": Topic.StatusChoices.PUBLISHED, "due_date": now - timedelta(days=5)},
            )
            self._set_dt(topic_lists, "created_at", now - timedelta(days=16))

            topic_dicts, _ = Topic.objects.get_or_create(
                unit=unit_data,
                name="Dictionaries & Sets",
                defaults={"sort_order": 2, "status": Topic.StatusChoices.DRAFT, "due_date": now + timedelta(days=7)},
            )
            self._set_dt(topic_dicts, "created_at", now - timedelta(days=2))

            TextContent.objects.get_or_create(
                topic=topic_lists,
                text_title="List Comprehension Patterns",
                defaults={"body": "[x*2 for x in range(10) if x % 2 == 0]\nResult: [0, 4, 8, 12, 16]", "format": "plain", "sort_order": 1},
            )
            LinkContent.objects.get_or_create(
                topic=topic_lists,
                display_text="Python List Comprehensions - Real Python",
                defaults={"url": "https://realpython.com/list-comprehension-python/", "sort_order": 2},
            )

            # --- DS Nest assessment ---
            ds_quiz, _ = Assessment.objects.get_or_create(
                nest=nest_ds,
                title="Quiz 1 - Arrays & Big-O",
                defaults={
                    "description": "Test your understanding of arrays and complexity.",
                    "assessment_type": "quiz",
                    "points": 15,
                    "due_date": now - timedelta(days=5),
                    "created_by": users["instructor_ali"],
                },
            )
            self._set_dt(ds_quiz, "created_at", now - timedelta(days=20))

            dq1, _ = Question.objects.get_or_create(
                assessment=ds_quiz,
                text="What is the time complexity of binary search?",
                defaults={"question_type": "mcq", "points": 5},
            )
            dq2, _ = Question.objects.get_or_create(
                assessment=ds_quiz,
                text="Describe when you would use a two-pointer approach.",
                defaults={"question_type": "text", "points": 10},
            )
            dc1, _ = Choice.objects.get_or_create(question=dq1, text="O(log n)", defaults={"is_correct": True})
            Choice.objects.get_or_create(question=dq1, text="O(n)", defaults={"is_correct": False})
            Choice.objects.get_or_create(question=dq1, text="O(n^2)", defaults={"is_correct": False})

            sub_hamad, _ = Submission.objects.get_or_create(assessment=ds_quiz, student=users["student_hamad"], defaults={"score": 13})
            self._set_dt(sub_hamad, "submitted_at", now - timedelta(days=4))
            Answer.objects.get_or_create(submission=sub_hamad, question=dq1, defaults={"selected_choice": dc1, "is_correct": True})
            Answer.objects.get_or_create(submission=sub_hamad, question=dq2, defaults={"text_answer": "When searching from both ends toward the center to avoid O(n^2).", "is_correct": True})

            # --- Additional quiz questions for CS101 ---
            q3, _ = Question.objects.get_or_create(
                assessment=quiz,
                text="What keyword is used to define a function in Python?",
                defaults={"question_type": "mcq", "points": 5},
            )
            q4, _ = Question.objects.get_or_create(
                assessment=quiz,
                text="Write a loop that prints numbers 1 to 5.",
                defaults={"question_type": "text", "points": 5},
            )
            c3, _ = Choice.objects.get_or_create(question=q3, text="def", defaults={"is_correct": True})
            Choice.objects.get_or_create(question=q3, text="func", defaults={"is_correct": False})
            Choice.objects.get_or_create(question=q3, text="function", defaults={"is_correct": False})

            # Sara submits quiz
            sub_sara, _ = Submission.objects.get_or_create(assessment=quiz, student=users["student_sara"], defaults={"score": 15})
            self._set_dt(sub_sara, "submitted_at", now - timedelta(days=12))
            Answer.objects.get_or_create(submission=sub_sara, question=q1, defaults={"selected_choice": c1, "is_correct": True})
            Answer.objects.get_or_create(submission=sub_sara, question=q2, defaults={"text_answer": "Functions let us reuse code and reduce repetition.", "is_correct": True})
            Answer.objects.get_or_create(submission=sub_sara, question=q3, defaults={"selected_choice": c3, "is_correct": True})
            Answer.objects.get_or_create(submission=sub_sara, question=q4, defaults={"text_answer": "for i in range(1, 6): print(i)", "is_correct": True})

            # Omar also answers new questions
            Answer.objects.get_or_create(submission=sub_omar, question=q3, defaults={"selected_choice": c3, "is_correct": True})
            Answer.objects.get_or_create(submission=sub_omar, question=q4, defaults={"text_answer": "for i in range(1, 6):\n    print(i)", "is_correct": True})

            # --- Rejected membership (moderation demo) ---
            rejected_user = users["student_lina"]
            rejected_membership, _ = NestMembership.objects.get_or_create(
                nest=nest_ds,
                user=rejected_user,
                defaults={"role": NestMembership.Role.MEMBER, "status": NestMembership.Status.REJECTED},
            )
            rejected_membership.status = NestMembership.Status.REJECTED
            rejected_membership.save(update_fields=["status"])
            self._set_dt(rejected_membership, "joined_at", now - timedelta(days=10))

            # --- Unapproved comment (moderation demo) ---
            unapproved_post = posts[3]  # "Mock exam tips for week 8"
            Comment.objects.get_or_create(
                post=unapproved_post,
                user=users["student_hamad"],
                content="Can we also get a practice exam from last year?",
                parent=None,
                defaults={"approved": False, "is_verified": False},
            )

            # --- Profile about texts ---
            about_texts = {
                "instructor_ali": "Computer Science instructor with 8 years of experience. Passionate about making programming accessible to everyone.",
                "assistant_noor": "Graduate TA specializing in algorithms and Python. Here to help you succeed.",
                "student_omar": "Second-year CS student. Interested in backend development and competitive programming.",
                "student_sara": "Studying CS with a focus on data science. Love collaborative learning.",
                "student_hamad": "Bootcamp enthusiast. Working through data structures one problem at a time.",
                "student_lina": "Freshman exploring programming for the first time.",
                "site_staff": "Platform administrator.",
            }
            for username, about in about_texts.items():
                user = users[username]
                profile = user.profile
                if not profile.about:
                    profile.about = about
                    profile.save(update_fields=["about"])

            # --- Recognition snapshots ---
            rec_data = [
                ("student_lina", nest_public, 72, "Early Explorer", "Community Starter"),
                ("student_omar", nest_python, 130, "Core Member", "Problem Solver"),
                ("student_sara", nest_python, 88, "Top Contributor", "Discussion Starter"),
                ("student_hamad", nest_ds, 64, "Engaged Member", "Collaborator"),
            ]
            for username, nest, score, title, badge in rec_data:
                rec, _ = NestRecognition.objects.get_or_create(user=users[username], nest=nest)
                rec.score = score
                rec.title = title
                rec.badge = badge
                rec.save(update_fields=["score", "title", "badge"])

            # --- Notifications (mix old/new + read/unread) ---
            notif_data = [
                ("student_lina", "Welcome to the Public Nest. Start with the pinned post and the orientation topic.", f"/nests/{nest_public.pk}/posts/", False, 0),
                ("student_sara", "New discussion in Public Nest: How to explore the demo.", f"/nests/{nest_public.pk}/posts/", False, 2),
                ("student_omar", "Announcement: Lab moved to Thursday.", f"/nests/{nest_python.pk}/posts/", False, 0),
                ("student_omar", "New reply on your loop question.", f"/nests/{nest_python.pk}/posts/", False, 1),
                ("student_omar", "Quiz 1 score has been published.", f"/nests/{nest_python.pk}/assessments/", True, 12),
                ("student_sara", "Assignment 2 is due in 5 days.", f"/nests/{nest_python.pk}/assessments/", False, 0),
                ("student_hamad", "New discussion in Data Structures Bootcamp.", f"/nests/{nest_ds.pk}/posts/", True, 6),
            ]
            for username, message, link, is_read, days_ago in notif_data:
                notif, _ = Notification.objects.get_or_create(
                    user=users[username],
                    message=message,
                    defaults={"link": link, "is_read": is_read},
                )
                notif.link = link
                notif.is_read = is_read
                notif.save(update_fields=["link", "is_read"])
                self._set_dt(notif, "created_at", now - timedelta(days=days_ago, hours=2))

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write("Demo users password: DemoPass123!")
        self.stdout.write("Suggested logins: instructor_ali, assistant_noor, student_omar, student_sara")
