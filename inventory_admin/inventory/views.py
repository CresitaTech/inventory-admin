from django.shortcuts import render

# Create your views here.
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OnHandBalanceReport, PaidInvoices
from .serializers import OnHandBalanceReportSerializer, CycleCountSerializer
from io import BytesIO
import math

class OnHandBalanceReportView(APIView):
    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file, sheet_name="On Hand Balance report")
        except Exception:
            return Response({'error': 'Sheet "On Hand Balance report" not found in the Excel file.'}, status=status.HTTP_400_BAD_REQUEST)

        df.columns = [col.strip() for col in df.columns]

        # Ensure numeric fields are clean
        # numeric_fields = ['Quantity', 'Allocated', 'Available', 'Price', 'Value']
        # for field in numeric_fields:
        #     df[field] = pd.to_numeric(df.get(field), errors='coerce').fillna(0)

        new_objects = []
        inserted = 0
        skipped = 0

        for _, row in df.iterrows():
            data = {
                'warehouse': str(row['Warehouse']).strip(),
                'location': str(row['Location']).strip(),
                'quantity': float(row['Quantity']) if pd.notna(row['Quantity']) else 0.0,
                'item_number': str(row['Item Number']).strip(),
                'available': float(row['Available']) if pd.notna(row['Available']) else 0.0,
                "value": float(row['Value']) if pd.notna(row['Value']) else 0.0,
                'price': float(row['Price']) if pd.notna(row['Price']) else 0.0,
            }

            # Check for duplicates based on all fields
            if not OnHandBalanceReport.objects.filter(
                warehouse=data['warehouse'],
                location=data['location'],
                item_number=data['item_number'],
                quantity=data['quantity'],
                available=data['available'], 
                value=data['value'], 
                price=data['price'], 
                
            ).exists():

                new_objects.append(OnHandBalanceReport(
                    item_number=row.get("Item Number", ""),
                    location=row.get("Location", ""),
                    warehouse=row.get("Warehouse", ""),
                    type=row.get("Type", ""),
                    currency=row.get("Currency", ""),
                    Commodity=row.get("Commodity", ""),
                    name=row.get("Name", ""),
                    gl_acount=float(row.get("GL Account", 0)) if pd.notna(row.get("GL Account", 0)) else 0.0,
                    storage_on_hand=row.get("Storage On Hand", ""),
                    quantity=float(row.get("Quantity", 0)) if pd.notna(row.get("Quantity", 0)) else 0.0,
                    allocated=float(row.get("Allocated", 0)) if pd.notna(row.get("Allocated", 0)) else 0.0,
                    available=float(row.get("Available", 0)) if pd.notna(row.get("Available", 0)) else 0.0,
                    uom=row.get("UOM", ""),
                    price = row.get("Price", ""),
                    value=float(row.get("Value", 0)) if pd.notna(row.get("Value", 0)) else 0.0,
                    aisle=row.get("Aisle", ""),
                    bin=row.get("Bin", ""),
                    level=row.get("Level", ""),
                    created_by=row.get("Created By", ""),
                ))
                inserted += 1
                # break
            else:
                skipped += 1
        # print("all_data", new_objects)

        OnHandBalanceReport.objects.bulk_create(new_objects, batch_size=1000)

        serializer = OnHandBalanceReportSerializer(OnHandBalanceReport.objects.all(), many=True)

        return Response({
            'inserted': inserted,
            'skipped': skipped,
            'data': serializer.data
        })


from rest_framework.generics import ListAPIView

class FetchOnHandBalanceReportView(ListAPIView):
    queryset = OnHandBalanceReport.objects.all()
    serializer_class = OnHandBalanceReportSerializer
    
    
    

from .serializers import ProjectedObsolescenceSerializer
from .models import ProjectedObsolescence
from datetime import datetime
from collections import defaultdict

class ProjectedObsolescenceView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            xl = pd.ExcelFile(file)
        except Exception as e:
            return Response({'error': f'Failed to read Excel file. {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        inserted = 0
        skipped = 0
        all_valid_records = []
        seen_records = set()  # <--- For tracking duplicates in current upload

        for sheet_name in xl.sheet_names:
            if sheet_name not in ["Projected Obsolescence (SF)", "Projected Obsolescence (NC)"]:
                continue

            df = xl.parse(sheet_name)
            df.columns = [col.strip() for col in df.columns]

            column_map_sf = {
                'Warehouse': 'warehouse',
                'Location': 'location',
                'Item #': 'item_number',
                'Item Name': 'item_name',
                'Lot #': 'lot_number',
                'Expiration Date': 'expiration_date',
                'Qty': 'quantity',
                'UOM': 'uom',
                'PRICE': 'price',
                'VALUE': 'value',
            }

            column_map_nc = column_map_sf.copy()
            if sheet_name == "Projected Obsolescence (NC)":
                column_map_nc.pop('Item #', None)
                df['Item #'] = ''  # To satisfy model requirement

            df.rename(columns=column_map_sf if sheet_name == "Projected Obsolescence (SF)" else column_map_nc, inplace=True)

            df['expiration_date'] = pd.to_datetime(df['expiration_date'], errors='coerce').dt.date
            df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
            df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
            df['value'] = pd.to_numeric(df['value'], errors='coerce').fillna(0)

            for _, row in df.iterrows():
                if pd.isna(row['expiration_date']) or row['expiration_date'] <= datetime.today().date():
                    continue

                unique_key = (
                    row.get('item_number', ''),
                    row.get('lot_number', ''),
                    row.get('expiration_date'),
                    row.get('warehouse', '')
                )

                if unique_key in seen_records:
                    skipped += 1
                    continue
                seen_records.add(unique_key)

                exists = ProjectedObsolescence.objects.filter(
                    item_number=unique_key[0],
                    lot_number=unique_key[1],
                    expiration_date=unique_key[2],
                    warehouse=unique_key[3],
                ).exists()

                if not exists:
                    record = ProjectedObsolescence.objects.create(
                        warehouse=row.get('warehouse', ''),
                        location=row.get('location', ''),
                        item_number=row.get('item_number', ''),
                        item_name=row.get('item_name', ''),
                        lot_number=row.get('lot_number', ''),
                        expiration_date=row.get('expiration_date'),
                        quantity=row.get('quantity', 0),
                        uom=row.get('uom', ''),
                        price=row.get('price', 0),
                        value=row.get('value', 0),
                    )
                    inserted += 1
                    all_valid_records.append(record)
                else:
                    skipped += 1

        serializer = ProjectedObsolescenceSerializer(all_valid_records, many=True)
        return Response({
            "inserted": inserted,
            "skipped": skipped,
            "data": serializer.data
        })
    
   
    def get(self, request):
        from datetime import date
        today = date.today()
        records = ProjectedObsolescence.objects.filter(expiration_date__gt=today)
        serializer = ProjectedObsolescenceSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
from .models import CycleCount
from decimal import Decimal, InvalidOperation
    
class CycleCountView(APIView):
    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            xl = pd.ExcelFile(file)
            if "Cycle Count" not in xl.sheet_names:
                return Response({"error": "Sheet 'Cycle Count' not found."}, status=status.HTTP_400_BAD_REQUEST)

            df = xl.parse("Cycle Count")
        except Exception as e:
            return Response({"error": f"Failed to read sheet: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        df.columns = [col.strip() for col in df.columns]

        required_columns = [
            'Cycle Count #', 'Warehouse', 'Number of lines', 'Total Value',
            'Currency', 'Created By', 'Created Date', 'Discrepancy Lines',
            'Status', '%'
        ]
        for col in required_columns:
            if col not in df.columns:
                return Response({"error": f"Missing column: {col}"}, status=status.HTTP_400_BAD_REQUEST)

        inserted, skipped = 0, 0
        all_valid = []
        count = 0
        total_rows = len(df)

        for _, row in df.iterrows():
            try:
                def to_decimal(val):
                    try:
                        return Decimal(str(val).replace(',', '').strip())
                    except (InvalidOperation, TypeError):
                        return Decimal('0')

                value  = row.get('%', '0')
                percentage_val = value * 100
                # break

                cycle_count_val = to_decimal(row.get('Cycle Count #', 0))
                number_of_lines_val = to_decimal(row.get('Number of lines', 0))
                total_value_val = to_decimal(row.get('Total Value', 0))
                discrepancy_lines_val = to_decimal(row.get('Discrepancy Lines', 0))

                exists = CycleCount.objects.filter(
                    warehouse=row.get('Warehouse', ''),
                    number_of_lines=number_of_lines_val,
                    total_value=total_value_val,
                    currency=row.get('Currency', ''),
                    created_by=row.get('Created By', ''),
                    created_date=row.get('Created Date', None),
                    status=row.get('Status', '')
                ).exists()

                if not exists:
                    record = CycleCount.objects.create(
                        cycle_count=cycle_count_val,
                        warehouse=row.get('Warehouse', ''),
                        number_of_lines=number_of_lines_val,
                        total_value=total_value_val,
                        currency=row.get('Currency', ''),
                        created_by=row.get('Created By', ''),
                        created_date=row.get('Created Date', None),
                        discrepancy_lines=discrepancy_lines_val,
                        status=row.get('Status', ''),
                        percentage=percentage_val
                    )
                    
                    inserted += 1
                    all_valid.append(record)
                    
                    count += 1
                    if count % 500 == 0 or count == total_rows:
                        print(f"[INFO] Inserted {count}/{total_rows} records...")    
                   
                else:
                    skipped += 1
                
            except Exception as e:
                skipped += 1
                continue

        serializer = CycleCountSerializer(all_valid, many=True)
        return Response({
            "inserted": inserted,
            "skipped": skipped,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    def get(self, request):
        records = CycleCount.objects.all()
        serializer = CycleCountSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
from .models import CarryingCost

class CarryingCostView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        
        if not file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Read the Excel file and target the specific sheet
            df = pd.read_excel(file, sheet_name="Inventory carrying cost")
        except Exception as e:
            return Response({"error": f"Error reading Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        required_columns = [
            'Warehouse', 'Storage', 'Total Inventory Value', 
            'Date', 'Handling', 'Loss', 'Damage'
        ]

        # Check if all required columns are present
        # if not all(col in df.columns for col in required_columns):
        #     return Response({"error": "Missing required columns in the sheet."}, status=status.HTTP_400_BAD_REQUEST)
        
        inserted_records = []

        for _, row in df.iterrows():
            # Clean row values
            print("roww", row)
            data = {
                'warehouse': row['Warehouse'],
                'storage': row['Storage'],
                'total_inventory_value': row['Total Inventory Value'],
                'date': str(row['Date']),
                'handling': row['Handling'],
                'loss': row.get('Loss'),
                'damage': row.get('Damage') 
            }

            # Check for duplicates based on all fields
            if not CarryingCost.objects.filter(
                warehouse=data['warehouse'],
                storage=data['storage'],
                total_inventory_value=data['total_inventory_value'],
                date=data['date'],
                handling=data['handling'],
                loss=data['loss'],
                damage=data['damage']
            ).exists():
                obj = CarryingCost.objects.create(**data)
                inserted_records.append({
                    'id': obj.id,
                    **data
                })

        return Response({
            "inserted_count": len(inserted_records),
            "inserted_data": inserted_records
        }, status=status.HTTP_201_CREATED)
        
   
    def get(self, request):
        from .serializers import CarryingCostSerializer
        records = CarryingCost.objects.all()
        serializer = CarryingCostSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


from .models import InventoryOutstanding
class InventoryOutstandingView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        
        if not file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Read the Excel file and target the specific sheet
            df = pd.read_excel(file, sheet_name="Inventory Outstanding")
        except Exception as e:
            return Response({"error": f"Error reading Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        required_columns = [
            'Warehouse', 'Type', 'Active', 
            'Inventory Outstanding', 'Date'
        ]

        # Check if all required columns are present
        # if not all(col in df.columns for col in required_columns):
        #     return Response({"error": "Missing required columns in the sheet."}, status=status.HTTP_400_BAD_REQUEST)
        
        inserted_records = []

        for _, row in df.iterrows():
            data = {
                'warehouse': row['Warehouse'],
                'type': row['Type'],
                'active': row['Active'],
                'inventory_outstanding': row['Inventory Outstanding'],
                'date': row['Date']
            }

            # Check for duplicates based on all fields
            if not InventoryOutstanding.objects.filter(
                warehouse=data['warehouse'],
                inventory_outstanding=data['inventory_outstanding']
            ).exists():
                obj = InventoryOutstanding.objects.create(**data)
                inserted_records.append({
                    'id': obj.id,
                    **data
                })

        return Response({
            "inserted_count": len(inserted_records),
            "inserted_data": inserted_records
        }, status=status.HTTP_201_CREATED)
        
        
    def get(self, request):
        from .serializers import InventoryOutstandingSerializer
        records = InventoryOutstanding.objects.all()
        serializer = InventoryOutstandingSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



class PaidInvoicesView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file, sheet_name='Raw Data')

            # Standardize column names (strip whitespace)
            df.columns = df.columns.str.strip()

            inserted_records = []
            count = 0
            total_rows = len(df)
            for _, row in df.iterrows():
                invoice_id = int(row.get('Invoice ID'))

                if PaidInvoices.objects.filter(invoice_id=invoice_id).exists():
                    continue  # Skip duplicates

                record = PaidInvoices.objects.create(
                    po_number=str(row.get('PO Number', '')).strip(),
                    req_number=str(row.get('Req #', '')).strip(),
                    contract_punchout_user=str(row.get('Contract/Punchout/User', '')).strip(),
                    invoice_id=invoice_id,
                    invoice_number=str(row.get('Invoice #', '')).strip(),
                    invoice_date=str(row.get('Invoice Date', '')).strip(),
                    supplier=str(row.get('Supplier', '')).strip(),
                    total=row.get('Total') or 0.00,
                    payment_term=str(row.get('Payment Term', '')).strip(),
                    status=str(row.get('Status', '')).strip(),
                    requester=str(row.get('Requester', '')).strip(),
                    current_approver=str(row.get('Current Approver', '')).strip(),
                    date_received=str(row.get('Date Received', '')).strip(),
                    created_date=str(row.get('Created Date', '')).strip(),
                    net_due_date=str(row.get('Net Due Date', '')).strip(),
                    discount_due_date=str(row.get('Discount Due Date', '')).strip(),
                    payment_date=str(row.get('Payment Date', '')).strip(),
                    epd_potential=str(row.get('EPD Potential', '')).strip(),
                    delivery_method=str(row.get('Delivery Method', '')).strip(),
                    pricing_bucket=str(row.get('Pricing Bucket', '')).strip(),
                )

                inserted_records.append({
                    'invoice_id': record.invoice_id,
                    'supplier': record.supplier,
                    'total': str(record.total)
                })
                
                count += 1
                if count % 500 == 0 or count == total_rows:
                    print(f"[INFO] Inserted {count}/{total_rows} records...")

            return Response({
                'message': f'{len(inserted_records)} records inserted.',
                'inserted': inserted_records
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

    def get(self, request):
        from .serializers import PaidInvoicesSerializer
        invoices = PaidInvoices.objects.all()
        serializer = PaidInvoicesSerializer(invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_boldbi_url(request):
    try:
        url = "https://cloud.boldbi.com/bi/api/system-settings/get-url"

        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWJlZF91c2VyX2VtYWlsIjoidmlyYWpAY3Jlc2l0YXRlY2guY29tIiwiZW1iZWRfdXNlcl9uYW1lIjoidmlyYWpAY3Jlc2l0YXRlY2guY29tIiwiaXNzIjoiZW1iZWQiLCJleHAiOjE3NTA1OTQwMzl9.dkNgxr9Za5xae5W3_7raMQII2UWHam3eMU3Vh-2dR40",  # replace this with your actual token
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)

        # Forward exact status and response
        return JsonResponse(response.json(), status=response.status_code)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    

class CustomFileUploadView(APIView):
    def post(self, request):
        custom_file = request.FILES.get('file')

        if not custom_file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Save the file (e.g., to MEDIA_ROOT/custom_uploads/)
            file_path = default_storage.save(f'custom_uploads/{custom_file.name}', ContentFile(custom_file.read()))
        except Exception as e:
            return Response({"error": f"Failed to store file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "Custom file uploaded successfully.",
            "file_path": file_path
        }, status=status.HTTP_201_CREATED)
        
        


import pandas as pd
from .models import CpoPaidInvoices
from datetime import datetime

def parse_date(date_str):
    try:
        if pd.isna(date_str) or str(date_str).strip() in ['#N/A', 'nan', '', 'NaT']:
            return None
        return pd.to_datetime(date_str).to_pydatetime()
    except Exception:
        return None
    


from decimal import Decimal, InvalidOperation

def parse_decimal(value):
    try:
        if pd.isna(value) or str(value).strip() in ['#N/A', 'nan', '', 'NaT']:
            return None
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


class CpoPaidInvoicesView(APIView):
    def post(self, request):
        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        df = pd.read_excel(excel_file)

        records = []
        for _, row in df.iterrows():
            record = CpoPaidInvoices(
                po_number=row.get('PO Number'),
                req_number=row.get('Req #'),
                order_date=parse_date(row.get('Order Date')),
                item=row.get('Item'),
                item_unit_price=parse_decimal(row.get('Item Unit price')),
                item_negotiated_price=parse_decimal(row.get('Item Negotiated price')),
                contract_punchout_user=row.get('Contract/Punchout/User'),
                invoice_id=row.get('Invoice ID'),
                invoice_number=row.get('Invoice #'),
                invoice_date=parse_date(row.get('Invoice Date')),
                supplier=row.get('Supplier'),
                total=parse_decimal(row.get('Total')),
                payment_term=row.get('Payment Term'),
                status=row.get('Status'),
                requester=row.get('Requester'),
                current_approver=row.get('Current Approver'),
                date_received_grn=parse_date(row.get('Date Received- GRN')),
                invoice_created_date=parse_date(row.get('Invoice Created Date')),
                net_due_date=parse_date(row.get('Net Due Date')),
                discount_due_date=parse_date(row.get('Discount Due Date')),
                payment_date=parse_date(row.get('Payment Date')),
                epd_potential=row.get('EPD Potential'),
                delivery_method=row.get('Delivery Method'),
                pricing_bucket=row.get('Pricing Bucket')
            )
            records.append(record)

        CpoPaidInvoices.objects.bulk_create(records, batch_size=500)
        return Response({"message": f"{len(records)} records uploaded successfully."}, status=status.HTTP_201_CREATED)
    

from .serializers import UploadInventoryDataSerializer
class UploadInventoryDataView(APIView):
    def post(self, request):
        serializer = UploadInventoryDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Data inserted successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)