import requests
import bs4
import splinter
from splinter import Browser
from dataclasses import dataclass
import time

class SupremeBot:

    def __init__(self):
        self.base = 'https://supremenewyork.com/'
        self.shop = 'shop/all/'
        self.checkout_extension = 'checkout/'
        self.info = ''
        self.fill_fields = [
        'order[billing_name]',
        'order[email]',
        'order[tel]',
        'order[billing_address]',
        'order[billing_city]',
        'order[billing_zip]',
        'credit_card[number]',
        'credit_card[verification_value]']

        self.select_fields = [
        'order[billing_country]',
        'credit_card[type]',
        'credit_card[month]',
        'credit_card[year]']
    
    @dataclass
    class Select:
        '''Dataclass representing personal information for the select fields.'''
        country: str
        card: str
        month: str
        year: str

        def to_array(self) -> list:
            array = [self.country,
            self.card,
            self.month,
            self.year]
            return array

    @dataclass
    class Fill:
        '''Dataclass representing personal information for the fill fields.'''
        name: str
        email: str
        phone: str
        address: str
        city: str
        zip: str
        number: str
        ccv: str

        def to_array(self) -> list:
            array = [self.name,
            self.email,
            self.phone,
            self.address,
            self.city,
            self.zip,
            self.number,
            self.ccv]
            return array
    
    @dataclass
    class Credentials:
        '''Fill class and select class merged together.'''
        def __init__(self, select, fill):
            self.Select = select
            self.Fill = fill
    
    @dataclass
    class Product:
        '''Dataclass representing product on the supreme website'''
        name: str
        color: str
        size: str
        category: str
        status = ''
        final_link= ''

    def init_browser(self, browser_type:str):
        '''Initializing the browser: Firefox or Google Chrome'''
        if browser_type == 'firefox':
            executable_path = {'executable_path':'C:/Program Files/Mozilla Firefox/geckodriver.exe'}
        elif browser_type == 'chrome':
            executable_path = {'executable_path':'C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe'}
        else: raise ValueError('Wrong web browser!') 
        
        self.browser = Browser(browser_type, **executable_path)

    def visit_page(self, extension:str):
        self.browser.visit('{}{}'.format(self.base, extension))

    def find_product(self, product:Product):
        r = requests.get('{}{}{}'.format(self.base, self.shop, product.category)).text
        soup = bs4.BeautifulSoup(r, 'lxml')
        soup_tuple = [(x['href'], x.text) for x in soup.find_all('a', href=True)]

        soup_links= [a[0] for a in soup_tuple if a[1]==product.name]

        product.final_link=''.join([x[0] for y in soup_links for x in soup_tuple if x[0] == y and x[1] == product.color])

        #removing product that are sold out and prompt an info
        if product.final_link == '':
            product.status='Product or color not found.'
            return
        else:
            infos = [a[1] for a in soup_tuple if a[0] == product.final_link]
            if 'sold out' in infos:
                product.status='Product sold out.'
                return
            else:
                product.status='Product found.'
                return
   
    def add_to_basket(self, product:Product):
            try:      
                self.browser.visit('{}{}'.format(self.base, str(product.final_link)))
                if(product.size != ''): self.browser.find_option_by_text(product.size).click()
                self.browser.find_by_value('add to basket').click()
                product.status = 'Product added to basket.'
                self.browser.find_by_value('keep shopping').click()
                return
            except splinter.exceptions.ElementDoesNotExist: 
                product.status = 'Size not available'
                return

    def checkout(self, credentials:Credentials):
        self.visit_page(self.checkout_extension)
        [self.browser.select(self.select_fields[x], credentials.Select.to_array()[x]) for x in range(len(self.select_fields))]
        [self.browser.fill(self.fill_fields[x], credentials.Fill.to_array()[x]) for x in range(len(self.fill_fields))]
        self.browser.find_by_css('.terms').click()
        #!!!BUY BUY BUY BUY!!!
        #self.browser.find_by_value('process payment').click()

    def execute(self, products:list, credentials:Credentials, browser_type:str):
        
        self.init_browser(browser_type)
        
        [self.find_product(product) for product in products]
        [self.add_to_basket(product) for product in products if product.status=='Product found.']
        
        if any(x.status == 'Product added to basket.' for x in products):
            self.checkout(credentials)
        else: print('Basket is empty! Program cannot check out.')

def main():
    products = [
        ['Studded Velvet Hooded Work Jacket', 'Black', 'Large', 'jackets'],
        ['Plaid Flannel Shirt', 'Multicolor', 'Medium', 'shirts'],
        ['Supreme®/Hanes® Boxer Briefs (2 Pack)','Pink', 'Medium', 'accessories'],
    ]
    products = [SupremeBot.Product(
        product[0], product[1], product[2], product[3]) for product in products]

    credentials = SupremeBot.Credentials(
        SupremeBot.Select(
            country='PL',
            card='credit card',
            month='11',
            year='2022'),
        SupremeBot.Fill(
            name='cxvxc',
            email='john@email.com',
            phone='643264233',
            address='osdfshdsf 21',
            city='daf',
            zip='321321',
            number='4921 2134 2222 3333',
            ccv='123')
    )

    webbrowser = 'chrome'
    bot = SupremeBot()
    bot.execute(products, credentials, webbrowser)
    [print(product.name, product.color, product.status) for product in products]

if __name__ == '__main__': 
    
    start = time.time()
    main()
    end = time.time()
    print(end - start)
