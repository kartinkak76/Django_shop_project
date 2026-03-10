"""
URL конфигурация для приложения shop
"""
from django.urls import path
from . import views
from . import views_auth

app_name = 'shop'

urlpatterns = [
    # Главная страница
    path('', views.HomePageView.as_view(), name='home'),
    
    
    # Каталог
    # Список товаров
    path('products/', views.ProductListView.as_view(), name='product_list'),
    # Фильтр по категории
    path('category/<slug:category_slug>/', 
         views.ProductListView.as_view(), name='product_list_by_category'),
    # Фильтр по тегу
    path('tag/<slug:tag_slug>/', 
         views.ProductListView.as_view(), name='product_list_by_tag'),
    # Детальная страница товара
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),   
    
    
    # Информационный страницы
    # Страницы "О нас" и "Контакты"
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    # Список категорий
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    # Список тегов
    path('tags/', views.TagListView.as_view(), name='tag_list'),    


    # Управление товарами
    # Создание товара
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    # Редактирование товара
    path('product/<slug:slug>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    # Удаление товара
    path('product/<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    # Добавление отзыва
    path('product/<slug:product_slug>/review/add/', views.add_review, name='add_review'),
    

    # Корзина и оформление заказа
    path('cart/', views.cart_page, name='cart'),
    path('checkout/', views.checkout_page, name='checkout'),
    

    # === РАЗДЕЛ ПОДДЕРЖКИ ===
    # Публичные страницы
    path('support/create/', views.TicketCreateView.as_view(), name = 'ticket_create'),
    path('support/register', views.register_view, name='register'),
    
    # AJAX
    path('support/check-email/', views.check_email_ajax, name = 'check_email_ajax'),
    
    # Авторизованные пользователи
    path('support/my-tickets/', views.MyTicketsListView.as_view(), name = 'my_tickets'),
    path('support/ticket/<int:pk>/', views.TicketDetailView.as_view(), name = 'ticket_detail'),
    path('support/ticket/<int:pk>/edit', views.TicketUpdateView.as_view(), name = 'ticket_edit'),
    path('support/ticket/<int:pk>/delete/', views.TicketDeleteView.as_view(), name='ticket_delete'),
    path('support/ticket/<int:pk>/attach/', views.add_attachment, name='add_attachment'),
    
    # Админка
    path('support/admin/tickets/', views.AdminTicketListView.as_view(), name = 'admin_tickets'),
    path('support/admin/response/<int:pk>/', views.AdminResponseView.as_view(), name = 'admin_response'),

    # Авторизация и аккаунт
    # Регистрация нового пользователя
    path('auth/register/', views.register_view, name='register'),
    # Вход в аккаунт
    path('auth/login/', views_auth.login_view, name='login'),
    # Выход из аккаунта
    path('auth/logout/', views_auth.logout_view, name='logout'),
    # Личный кабинет
    path('account/profile/edit/', views_auth.profile_view, name='profile'),
    # Редактирование профиля
    path('account/profile/edit/', views_auth.profile_edit_view, name='profile_edit'),
    # Смена пароля
    path('account/password/change/', views_auth.password_change_view, name='password_change'),
]