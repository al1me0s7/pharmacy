class Page:
    def __init__(self, title):
        self.title = title
    
    def get_title(self):
        return self.title
    
    def show_header(self):
        return f'<header><h1>{self.title}</h1></header>'
    
    def show_content(self):
        return 'Контент сторінки'
    
    def show_footer(self):
        return 'Аптека © 2026'
    
    def render(self):
        return self.show_header() + self.show_content() + self.show_footer()

class MainPage(Page):
    """Головна сторінка — каталог ліків"""
    
    def __init__(self):
        super().__init__('Каталог ліків - Аптека')
    
    def show_content(self):
        return 'Каталог препаратів з фільтрами'

class MedicinePage(Page):
    """Сторінка окремого препарату"""
    def __init__(self, medicine_name):
        super().__init__(f'{medicine_name} - Аптека')
        self.medicine_name = medicine_name
    
    def show_content(self):
        return f'Детальна інформація про {self.medicine_name}'

class CartPage(Page):
    """Сторінка кошика"""
    
    def __init__(self):
        super().__init__('Кошик - Аптека')
    
    def show_content(self):
        return 'Товари у кошику'

class ProfilePage(Page):
    """Сторінка профілю користувача"""
    
    def __init__(self, user_name):
        super().__init__(f'Профіль: {user_name}')
        self.user_name = user_name
    
    def show_content(self):
        return f'Профіль користувача {self.user_name}'