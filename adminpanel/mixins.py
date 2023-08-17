from django.contrib.auth.mixins import UserPassesTestMixin


class SuperuserRequiredMixin(UserPassesTestMixin):
    """
    Check if the user is a superuser (admin) or not.
    """

    def test_func(self):
        return self.request.user.is_superuser
