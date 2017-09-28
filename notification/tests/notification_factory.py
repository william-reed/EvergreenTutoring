from factory.django import DjangoModelFactory
from notification.models import Notification, DeliveryInfo
from profile.tests.user_factory import UserFactory
from factory import Faker, SubFactory


class NotificationFactory(DjangoModelFactory):
    """
    Notification Factory

    Throws some random latin into subject and message
    """

    class Meta:
        model = Notification

    from_user = SubFactory(UserFactory)
    author = 'Notification Author'
    subject = Faker('sentence', nb_words=5)
    message = Faker('sentence', nb_words=75)


class DeliveryInfoFactory(DjangoModelFactory):
    """
    Delivery Info Factory. nothing interesting to see here
    """

    class Meta:
        model = DeliveryInfo

    notification = SubFactory(NotificationFactory)
    to_user = UserFactory()
