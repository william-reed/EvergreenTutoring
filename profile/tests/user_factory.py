from factory.django import DjangoModelFactory
import factory
from django.contrib.auth.models import User
from profile.models import Profile
from django.db.models.signals import post_save


class ProfileFactory(DjangoModelFactory):
    """
    Profile factory populated with fake information
    """

    class Meta:
        model = Profile

    street_address = factory.Faker('street_address')
    city = factory.Faker('city')
    state = factory.Faker('state')
    zip = factory.Faker('random_number', digits=5)
    user = factory.SubFactory('profile.tests.user_factory.UserFactory', profile=None)


# disable so we can create the Profile on our own
@factory.django.mute_signals(post_save)
class UserFactory(DjangoModelFactory):
    """
    User Factory populated with fake information
    """

    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    # user0, user1, user2, etc
    username = factory.Sequence(lambda n: 'user%d' % n)
    email = factory.Faker('email')
    profile = factory.RelatedFactory(ProfileFactory, 'user')
