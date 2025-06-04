from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from stocks.models import StockPrice, Company, Subscriber
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send daily market report email to subscribers'
    
    def handle(self, *args, **options):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get today's latest stock prices
        today_prices = StockPrice.objects.filter(date=today).order_by('symbol', '-time')
        
        # If no prices for today, try yesterday's data
        if not today_prices.exists():
            self.stdout.write(self.style.WARNING(f"No stock prices found for {today}, using {yesterday}'s data"))
            today = yesterday
            today_prices = StockPrice.objects.filter(date=yesterday).order_by('symbol', '-time')
            
            if not today_prices.exists():
                self.stdout.write(self.style.ERROR(f"No stock data available for reporting"))
                return
        
        # Get unique latest prices (one per symbol)
        latest_prices = {}
        for price in today_prices:
            if price.symbol not in latest_prices:
                latest_prices[price.symbol] = price
        
        # Get yesterday's closing prices for comparison
        yesterday_prices = {}
        yesterday_data = StockPrice.objects.filter(date=yesterday).order_by('symbol', '-time')
        for price in yesterday_data:
            if price.symbol not in yesterday_prices:
                yesterday_prices[price.symbol] = price
        
        # Prepare stock data with changes
        stocks_data = []
        for symbol, price in latest_prices.items():
            yesterday_price = yesterday_prices.get(symbol)
            change = 0
            percent_change = 0
            
            if yesterday_price:
                change = price.price - yesterday_price.price
                if yesterday_price.price > 0:
                    percent_change = (change / yesterday_price.price) * 100
            
            stocks_data.append({
                'symbol': symbol,
                'price': price.price,
                'change': change,
                'percent_change': percent_change,
                'volume': price.volume or 0,
                'value': price.value or 0,
            })
        
        # Sort by percent change to get top movers
        stocks_data.sort(key=lambda x: abs(x['percent_change']), reverse=True)
        top_movers = stocks_data[:5]
        
        # Calculate market summary
        gainers = sum(1 for stock in stocks_data if stock['change'] > 0)
        losers = sum(1 for stock in stocks_data if stock['change'] < 0)
        unchanged = sum(1 for stock in stocks_data if stock['change'] == 0)
        total_value = sum(stock['value'] for stock in stocks_data)
        total_volume = sum(stock['volume'] for stock in stocks_data)
        
        market_summary = {
            'total_value': total_value,
            'total_volume': total_volume,
            'gainers': gainers,
            'losers': losers,
            'unchanged': unchanged,
        }
        
        # Format date nicely
        formatted_date = today.strftime("%A, %B %d, %Y")
        
        # Prepare email context
        context = {
            'date': formatted_date,
            'summary': market_summary,
            'top_movers': top_movers,
            'stocks': sorted(stocks_data, key=lambda x: x['symbol']),
            'current_year': today.year,
            'unsubscribe_url': 'https://mse-watch.onrender.com/unsubscribe/',
        }
        
        # Render email templates
        html_content = render_to_string('stocks/email/daily_report.html', context)
        text_content = render_to_string('stocks/email/daily_report.txt', context)
        
        # Get subscribers
        subscribers = Subscriber.objects.filter(is_active=True)
        
        if not subscribers.exists():
            self.stdout.write(self.style.WARNING("No active subscribers found"))
            
        # Send emails
        success_count = 0
        for subscriber in subscribers:
            try:
                subject = f"MSE Daily Market Report - {formatted_date}"
                email = EmailMultiAlternatives(
                    subject,
                    text_content,
                    from_email=None,  # Use DEFAULT_FROM_EMAIL from settings
                    to=[subscriber.email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send email to {subscriber.email}: {str(e)}")
        
        self.stdout.write(self.style.SUCCESS(
            f"Sent daily report to {success_count} of {subscribers.count()} subscribers"
        ))