import json
import csv
from django.core.management.base import BaseCommand
from datetime import datetime
from stocks.models import Company

class Command(BaseCommand):
    help = 'Import company data from JSON or CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to JSON or CSV file containing company data',
        )
        parser.add_argument(
            '--format',
            choices=['json', 'csv'],
            default='json',
            help='Format of the input file (json or csv)',
        )
    
    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        file_format = kwargs['format']
        
        self.stdout.write(f"Importing company data from {file_path}")
        
        try:
            if file_format == 'json':
                self.import_from_json(file_path)
            else:
                self.import_from_csv(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing data: {str(e)}"))
    
    def import_from_json(self, file_path):
        """Import company data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                companies_data = json.load(f)
            
            count = 0
            for company_data in companies_data:
                try:
                    # Handle date fields
                    if 'listed_date' in company_data and company_data['listed_date']:
                        try:
                            company_data['listed_date'] = datetime.strptime(company_data['listed_date'], '%Y-%m-%d').date()
                        except ValueError:
                            company_data['listed_date'] = None
                    
                    company, created = Company.objects.update_or_create(
                        symbol=company_data['symbol'],
                        defaults=company_data
                    )
                    count += 1
                    if created:
                        self.stdout.write(f"Created company record for {company_data['symbol']}")
                    else:
                        self.stdout.write(f"Updated company record for {company_data['symbol']}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing {company_data.get('symbol', 'unknown')}: {str(e)}"))
            
            self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} companies"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to open or parse file: {str(e)}"))
    
    def import_from_csv(self, file_path):
        """Import company data from CSV file"""
        try:
            with open(file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                
                count = 0
                for row in reader:
                    try:
                        # Handle empty strings for non-string fields
                        for field in ['founded_year', 'employees', 'shares_in_issue']:
                            if field in row and row[field] == '':
                                row[field] = None
                        
                        # Handle date fields
                        if 'listed_date' in row and row['listed_date']:
                            try:
                                row['listed_date'] = datetime.strptime(row['listed_date'], '%Y-%m-%d').date()
                            except ValueError:
                                row['listed_date'] = None
                        
                        # Handle decimal fields
                        if 'listing_price' in row and row['listing_price']:
                            try:
                                row['listing_price'] = float(row['listing_price'])
                            except ValueError:
                                row['listing_price'] = None
                        
                        company, created = Company.objects.update_or_create(
                            symbol=row['symbol'],
                            defaults=row
                        )
                        count += 1
                        if created:
                            self.stdout.write(f"Created company record for {row['symbol']}")
                        else:
                            self.stdout.write(f"Updated company record for {row['symbol']}")
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error importing {row.get('symbol', 'unknown')}: {str(e)}"))
                
                self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} companies"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to open or parse file: {str(e)}"))