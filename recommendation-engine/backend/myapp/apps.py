from django.apps import AppConfig

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    def ready(self):
        # This code will run once when Django starts
        # Important: It runs twice in development if you use auto-reloader
        print("Django server is starting...")
        from myapp.text_sql_agent import initialize_text_sql_agent
        initialize_text_sql_agent()
    
