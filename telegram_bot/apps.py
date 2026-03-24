from django.apps import AppConfig


class TelegramBotConfig(AppConfig):
    name = 'telegram_bot'
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Telegram bot'

def ready(self):
    '''Регистрация сигнала при запуске джанго'''
    import telegram_bot.signals
    
