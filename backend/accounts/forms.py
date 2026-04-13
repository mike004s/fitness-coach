from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class SignInForm(AuthenticationForm):
    """Login form using email + password."""
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'name@domain.com',
            'class': 'w-full bg-surface-container-highest border-none rounded-lg '
                     'py-4 pl-12 pr-4 text-sm font-body focus:ring-1 '
                     'focus:ring-primary/20 focus:bg-surface-bright transition-all '
                     'placeholder:text-outline-variant text-on-surface',
            'autocomplete': 'email',
        }),
        label='Email Address',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'w-full bg-surface-container-highest border-none rounded-lg '
                     'py-4 pl-12 pr-4 text-sm font-body focus:ring-1 '
                     'focus:ring-primary/20 focus:bg-surface-bright transition-all '
                     'placeholder:text-outline-variant text-on-surface',
            'autocomplete': 'current-password',
        }),
        label='Password',
    )

    error_messages = {
        'invalid_login': 'Invalid email or password. Please try again.',
        'inactive': 'This account is inactive.',
    }


class SignUpForm(UserCreationForm):
    """Registration form with name, email, and password."""
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'ALEX RIVERA',
            'class': 'w-full bg-surface-container-highest border-none '
                     'focus:ring-0 focus:bg-surface-bright p-4 font-headline '
                     'text-sm tracking-tight placeholder:text-white/10 '
                     'text-on-surface transition-all duration-300',
            'autocomplete': 'name',
        }),
        label='Full Identity',
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'ALEX@KINETIC.APP',
            'class': 'w-full bg-surface-container-highest border-none '
                     'focus:ring-0 focus:bg-surface-bright p-4 font-headline '
                     'text-sm tracking-tight placeholder:text-white/10 '
                     'text-on-surface transition-all duration-300',
            'autocomplete': 'email',
        }),
        label='Digital Anchor',
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••••••',
            'class': 'w-full bg-surface-container-highest border-none '
                     'focus:ring-0 focus:bg-surface-bright p-4 font-headline '
                     'text-sm tracking-tight placeholder:text-white/10 '
                     'text-on-surface transition-all duration-300',
            'autocomplete': 'new-password',
        }),
        label='Secure Protocol',
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••••••',
            'class': 'w-full bg-surface-container-highest border-none '
                     'focus:ring-0 focus:bg-surface-bright p-4 font-headline '
                     'text-sm tracking-tight placeholder:text-white/10 '
                     'text-on-surface transition-all duration-300',
            'autocomplete': 'new-password',
        }),
        label='Confirm Protocol',
    )

    class Meta:
        model = User
        fields = ('full_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.full_name = self.cleaned_data.get('full_name', '')
        # Auto-generate username from email local part to satisfy AbstractUser
        base_username = user.email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1
        user.username = username
        if commit:
            user.save()
        return user
