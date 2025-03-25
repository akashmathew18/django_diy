from django import forms
from django.contrib.auth.models import User
from .models import Post, Comment, UserProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, ButtonHolder, HTML
from taggit.forms import TagField

class PostForm(forms.ModelForm):
    # Add category choices to form
    TECHNOLOGY_CATEGORIES = Post.TECHNOLOGY_CATEGORIES
    SPORTS_CATEGORIES = Post.SPORTS_CATEGORIES

    class Meta:
        model = Post
        fields = ['title', 'category', 'content', 'featured_image', 'tags', 'status']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., technology, programming, web-development, python, django'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = True
        
        # Set default status to 'published'
        self.initial['status'] = 'published'
        
        # Make featured_image optional
        self.fields['featured_image'].required = False
        
        self.helper.layout = Layout(
            Field('title', css_class='form-control'),
            Field('category', css_class='form-control'),
            Field('content', css_class='form-control'),
            Field('featured_image', css_class='form-control'),
            Field('tags', css_class='form-control'),
            Field('status', css_class='form-control'),
            HTML('<small class="text-muted">Popular tags: technology, programming, web-development, python, django, javascript, html, css, react, vue, angular, database, api, security, testing, deployment</small>'),
            ButtonHolder(
                Submit('submit', 'Save Post', css_class='btn btn-primary')
            )
        )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your comment...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Field('content', css_class='form-control'),
            ButtonHolder(
                Submit('submit', 'Post Comment', css_class='btn btn-primary')
            )
        )

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content.strip():
            raise forms.ValidationError('Content cannot be empty.')
        return content

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Field('profile_picture', css_class='form-control'),
            Field('bio', css_class='form-control'),
            Field('website', css_class='form-control'),
            ButtonHolder(
                Submit('submit', 'Update Profile', css_class='btn btn-primary')
            )
        ) 

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True}),
        help_text='Your password must be at least 8 characters long.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True}),
        help_text='Enter the same password as above, for verification.'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
        help_text='Required. Enter a valid email address.'
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Tell us a little about yourself...'
        }),
        required=False
    )
    profile_picture = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('email', css_class='form-control'),
            Field('first_name', css_class='form-control'),
            Field('last_name', css_class='form-control'),
            Field('password1', css_class='form-control'),
            Field('password2', css_class='form-control'),
            Field('bio', css_class='form-control'),
            Field('profile_picture', css_class='form-control'),
            ButtonHolder(
                Submit('submit', 'Create Account', css_class='btn btn-primary w-100')
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        if password1 and len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': True
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('password', css_class='form-control'),
            Field('remember_me', css_class='form-check-input'),
            ButtonHolder(
                Submit('submit', 'Log In', css_class='btn btn-primary w-100')
            )
        )