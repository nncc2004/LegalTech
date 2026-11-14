from django.contrib.auth.decorators import user_passes_test


def solo_superusuario(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_superuser
    )(view_func)