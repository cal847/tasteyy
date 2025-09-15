from django import forms
from recipes.models import Recipe


class AddRecipeForm(forms.ModelForm):
    """
    Form to handle adding new recipes.
    """

    # Use the choices defined in the Recipe model
    CATEGORY_CHOICES = Recipe.CATEGORY_CHOICES
    DIET_CHOICES = Recipe.DIET_CHOICES

    # Multi-select fields for category and diet
    category = forms.MultipleChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'style': 'min-height: 140px; font-size: 1.1rem; padding: 8px;',
        }),
        help_text="Hold Ctrl (Cmd on Mac) to select multiple options."
    )

    diet = forms.MultipleChoiceField(
        choices=DIET_CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'style': 'min-height: 140px; font-size: 1.1rem; padding: 8px;',
        }),
        help_text="Hold Ctrl (Cmd on Mac) to select multiple options."
    )

    class Meta:
        model = Recipe
        fields = [
            'title',
            'image',
            'description',
            'ingredients',
            'extra_tips',
            'instructions',
            'servings',
            'cooking_time',
            'prep_time',
            'category',
            'diet',    
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'E.g., Classic Chapati',
                'class': 'form-control',
                'style': 'height: 40px; font-size: 1rem;',
            }),

            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/gif',
                'style': 'padding: 10px; border: 2px dashed rgba(122, 6, 6, 0.2); border-radius: 10px; background: #fdf6f0; cursor: pointer;',
            }),

            'description': forms.Textarea(attrs={
                'placeholder': 'Briefly describe the dish... E.g., Soft, puffed whole wheat flatbread...',
                'rows': 4,
                'class': 'form-control',
                'style': 'min-height: 140px; font-size: 1.1rem; padding: 16px 20px;',
            }),

            'ingredients': forms.Textarea(attrs={
                'placeholder': 'List each ingredient on a new line...\n- 2 cups whole wheat flour\n- 3/4 cup warm water',
                'rows': 8,
                'class': 'form-control',
                'style': 'min-height: 140px; font-size: 1.1rem; padding: 16px 20px;',
            }),

            'instructions': forms.Textarea(attrs={
                'placeholder': 'Write each step numbered...\n1. Mix flour and water.\n2. Knead for 10 minutes...',
                'rows': 10,
                'class': 'form-control',
                'style': 'min-height: 140px; font-size: 1.1rem; padding: 16px 20px;',
            }),

            'servings': forms.NumberInput(attrs={
                'placeholder': '4',
                'min': '1',
                'class': 'form-control',
                'style': 'height: 40px; font-size: 1rem; padding: 8px 12px; border-radius: 8px;',
            }),

            'cooking_time': forms.NumberInput(attrs={
                'placeholder': '30',
                'min': '0',
                'class': 'form-control',
                'style': 'height: 40px; font-size: 1rem; padding: 8px 12px; border-radius: 8px;',
            }),
        }               