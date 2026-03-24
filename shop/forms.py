"""
Формы для приложения магазина
"""
from django import forms
from .models import Product, Category, Tag, ProductReview, SupportTicket, SupportTicketAttachment
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ProductReviewForm(forms.ModelForm):
    """Форма для добавления отзыва"""
    
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} ★') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Напишите ваш отзыв...'
                }
            ),
        }
        labels = {
            'rating': 'Ваша оценка',
            'comment': 'Комментарий',
        }

class ProductSearchForm(forms.Form):
    """Форма поиска товаров"""
    
    search = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Поиск товаров...'
            }
        )
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Категория',
        empty_label='Все категории',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        label='Цена от',
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'От'})
    )
    
    max_price = forms.DecimalField(
        required=False,
        label='Цена до',
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'До'})
    )
    
    sort = forms.ChoiceField(
        choices=[
            ('', 'Сортировать по'),
            ('price_asc', 'Цена: по возрастанию'),
            ('price_desc', 'Цена: по убыванию'),
            ('name', 'Название'),
            ('rating', 'Рейтинг'),
            ('newest', 'Новинки'),
        ],
        required=False,
        label='Сортировка',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ProductCreateForm(forms.ModelForm):
    """Форма создания товара"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'price', 'discount_price',
            'category', 'tags', 'is_featured', 'stock_quantity'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
        def clean_price(self):
            """
            Валидация поля 'price'
            """
            price = self.cleaned_data.get('price')
            
            # Проверка 1- Цена не может быть отрицательной
            if price is not None and price < 0:
                raise ValidationError(" Цена не может быть отрицательной")
            # Проверка 2 - Цена не может быть слишком высокой
            if price is not None and price > 10000:
                raise ValidationError("Цена слишком высокая")
            
        def clean_discount_price(self):
            # Валидация поля 'discount price (Цена ПО СКИДКЕ)'
            discount_price = self.cleaned_data.get('discount_price')
            return discount_price
        
        def clean_name(self):
            # Валидация поля "Название товара"
            name = self.cleaned_data.get('name')
            if name and len(name) < 3:
                raise ValidationError("Название должно содержать минимум три символа")
            
            forbidden_words = ['тест', "спам","заглушка", "ошибка"]
            if any(word in name.lower() for word in forbidden_words):
                raise ValidationError("Название содержит запрещеннык слова!")
        
            if Product.objects.filter(name__iexact=name).exists():
                raise ValidationError("Товар с таким названием уже существует")
            
        def clean(self):
            """
            Кросс-валидация всех полей (Вызывается после всех clean)
            """
            cleaned_data = super().clean()
            price = cleaned_data.get('price')
            discount_price = cleaned_data.get('discount_price')
            stock_quantity = cleaned_data.get('stock_quantity')
            
            # Если имеется скидка, то должна быть указана и цена
            if discount_price and not price:
                self.add_error('price', "Укажите обычную цену при наличии скидки")
                
            # Товар с количеством 0 не может быть рекомендуемым
            if cleaned_data.get('is_featured') and stock_quantity == 0:
                self.add_error('stock_quantity', "Рекомендуемый товар должен быть в наличии!")
            
class ProductFilterForm(forms.Form):
    """Форма фильтрации товаров"""
    
    STATUS_CHOICES = [
        ('', 'Все статусы'),
        ('draft', 'Черновик'),
        ('published', 'Опубликован'),
        ('archived', 'В архиве'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        label='Статус',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    in_stock = forms.BooleanField(
        required=False,
        label='Только в наличии',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    has_discount = forms.BooleanField(
        required=False,
        label='Только со скидкой',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
class SupportTicketForm(forms.ModelForm):
    """Форма создания нового обращения"""
   
    # Дополнительное поле для потверждения email
    email_confirm = forms.EmailField(
        label="Подтвердите email",
        widget=forms.EmailInput(attrs={
                                'class':'form-control',
                                'placeholder': 'Повторите ваш email'}),
        help_text= "Введите тот же email для подтверждения"
    ) 
    
    # Согласие на обработку данных
    agree_to_terms = forms.BooleanField(
        label='Я согласен на обработку персональных данных',
        required= True,
        error_messages={ 'required': "Необходимо согласие на обработку данных"}
    )
   
    class Meta:
        model = SupportTicket
        fields = ['email', 'subject', 'category', 'message']
        widgets = {
            'email': forms.EmailInput(attrs={
                                        'class': 'form-control',
                                        'placeholder': 'your@mail.com',
                                        'id':'id_email' # для AJAX 
                                        }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Краткая тема обращения',
                'maxlength': '200'
            }),
            'category': forms.Select(attrs={
                'class':'form-select'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Подробно опишите вашу проблему...',
                'maxlength': '5000'
            }),
            }
       
        labels = {
           'email': 'Ваш email',
           'subject': 'Тема',
           'category': 'Категория',
           'message': 'Сообщение',
       }
       
        def clean_email_confirm(self):
            """Проверка совпадения email"""
            email = self.cleaned_data.get('email')
            email_confirm = self.cleaned_data.get('email_confirm')
            
            if email and email_confirm and email != email_confirm:
                raise ValidationError("Email адреса не совпадают!")
            return email_confirm
        
        def cleaned_subject(self):
            """Валидация темы обращения"""
            subject = self.cleaned_data.get('subject')
            
            # минимальная длина
            if len(subject) < 5:
                raise ValidationError("Тема должна содержать минимум 5 символов")
            
            # Проверка на запрещенные слова
            forbidden_words = ['спам', 'тест', 'фигня', 'бред']
            if any(word in subject.lower() for word in forbidden_words):
                raise ValidationError("Тема содержит недопусчтимые слова!")
            return subject
       
        def clean_message(self):
           """Валидация сообщения"""
           message = self.cleaned_data.get('message')
           
           # Минимальная длина
           if len(message) < 20:
               raise ValidationError("Сообщение должно содержать минимум 20 символов")
           
           # Проверка на повторяющиеся символы (защиту от спама)
           if len(set(message))< len(message) * 0.3:
               raise ValidationError("Сообщение содержит слишком много повторяющихся символов")
           return message
        
        def clean_email(self):
            """Проверка email на существование в базе"""
            email = self.cleaned_data.get('email')
            
            active_tickets = SupportTicket.object.filter(
                email = email,
                status__in = ['new', 'in_progress']
            ).count()
            
            if active_tickets >= 3:
                raise ValidationError(
                    "У вас уже есть 3 активных обращения"
                    "Дождитесь ответа по текущим вопросам"
                )
            return email

class SupportTicketAttachmentForm(forms.ModelForm):
    class Meta:
        model = SupportTicketAttachment
        fields = ['file', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder': 'Описание файла(необязательно)'
            }),
        }       
    
    def clean_file(self):
        """Проверка размера и типа файлов"""
        file = self.cleaned_data.get('file')
        
        if file:
            # Проверка наличия файла, только потом начинаем проверку
            # Максимальный размер не более 5 Мб
            
            if file.size > 5 * 1024 * 1024:
                raise ValidationError("Размер файла должен быть не более 5 Мб!")
            
            # Разрешенные расширения
            allowed_extencions = ['.jpg', '.png', '.jpeg', '.gif', '.doc', '.docx']
            ext = file.name.split('.')[-1].lower()
            if f'.{ext}' not in allowed_extencions:
                raise ValidationError(f'Недопустимый формат файла. Разрешены: {", ".join(allowed_extencions)}')
        
        return file
    
class SupportTicketUpdateForm(forms.ModelForm):
    """Форма редактирования обращения (для владельца)"""
    
    class Meta:
        model = SupportTicket
        fields = ['subject', 'message']
        widgets ={
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.TextInput(attrs={'class': 'form-control', 'rows': 6}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Нельзя редактировать, если обращение уже решено
        if self.instance and self.instance.is_resolved:
            for field in self.fields:
                self.fields[field].disabled = True
                
class SupportResponseForm(forms.ModelForm):
    """Форма ответа администрации"""
    
    send_notification = forms.BooleanField(
        label = 'Отправить уведомление на email',
        required=False,
        initial=True,
        help_text='Пользователь получит письмо с ответом'
    )
    
    class Meta:
        model = SupportTicket
        fields = ['status', 'priority', 'response', 'is_resolved', 'is_public']
        widgets = {
            'status': forms.Select(attrs={'class':'form-select'}), 
            'priority': forms.Select(attrs={'class':'form-select'}), 
            'response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Напишите ваш ответ...'}), 
            'is_resolved': forms.CheckboxInput(attrs={'class':'form-check-input'}), 
            'is_public': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }
        
class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    
    email = forms.EmailField(
        required=True,
        widget = forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    first_name = forms.CharField(
        max_length=30,
        required = True,
        widget = forms.TextInput(attrs={'class':'form-control'})
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget = forms.TextInput(attrs={'class':'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields['username'].widget.attrs.update({'class':'form-control'})
        self.fields['password1'].widget.attrs.update({'class':'form-control'})
        self.fields['password2'].widget.attrs.update({'class':'form-control'})