from django.shortcuts import render

# Create your views here.
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OnHandBalanceReport
from .serializers import OnHandBalanceReportSerializer, CycleCountSerializer
from io import BytesIO

class OnHandBalanceReportView(APIView):
    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file, sheet_name="On Hand Balance report")
        except Exception as e:
            return Response({'error': 'Sheet "On Hand Balance report" not found in the Excel file.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Clean column names
        df.columns = [col.strip() for col in df.columns]

        column_map = {
            'Item Number': 'item_number',
            'Location': 'location',
            'Warehouse': 'warehouse',
            'Type': 'type',
            'Created By': 'created_by',
            'Currency' : 'currency',
            'Commodity': 'Commodity',
            'GL Account': 'gl_acount',
            'Name': 'name',
            'Storage On Hand': 'storage_on_hand',
            'Quantity': 'quantity',
            'Allocated': 'allocated',
            'Available': 'available',
            'UOM': 'uom',
            'Price': 'price',
            'Value': 'value',
            'Aisle': 'aisle',
            'Bin': 'bin',
            'Level': 'level',
        }

        df.rename(columns=column_map, inplace=True)

        inserted = 0
        skipped = 0
        
        numeric_fields = ['quantity', 'allocated', 'available', 'price', 'value']
        for field in numeric_fields:
            df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)

        for _, row in df.iterrows():
            # Basic duplicate check (adjust fields as per your logic)
            exists = OnHandBalanceReport.objects.filter(
                item_number=row.get("item_number"),
                location=row.get("location"),
                warehouse=row.get("warehouse"),
                quantity=row.get("quantity"),
                available=row.get("available")
            ).exists()

            if not exists:
                OnHandBalanceReport.objects.create(
                    item_number=row.get("item_number", ""),
                    location=row.get("location", ""),
                    warehouse=row.get("warehouse", ""),
                    type=row.get("type", ""),
                    currency=row.get("currency", ""),
                    Commodity=row.get("Commodity", ""),
                    name=row.get("name", ""),
                    gl_acount=row.get("gl_acount", ""),
                    storage_on_hand=row.get("storage_on_hand", ""),
                    quantity=row.get("quantity", 0),
                    allocated=row.get("allocated", 0),
                    available=row.get("available", 0),
                    uom=row.get("uom", ""),
                    price=row.get("price", 0),
                    value=row.get("value", 0),
                    aisle=row.get("aisle", ""),
                    bin=row.get("bin", 0),
                    level=row.get("level", 0),
                    created_by=row.get("created_by", ""),
                )
                inserted += 1
            else:
                skipped += 1

        # Return all data
        records = OnHandBalanceReport.objects.all()
        serializer = OnHandBalanceReportSerializer(records, many=True)
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

        for _, row in df.iterrows():
            try:
                def to_decimal(val):
                    try:
                        return Decimal(str(val).replace(',', '').strip())
                    except (InvalidOperation, TypeError):
                        return Decimal('0')

                # Just strip the '%' sign, nothing else
                # percentage_raw = str(row.get('%', '0')).replace('%', '').strip()
                # percentage_val = to_decimal(percentage_raw)
                # print(percentage_val)
                value  = row.get('%', '0')
                percentage_val = value * 100
                # break

                cycle_count_val = to_decimal(row['Cycle Count #'])
                number_of_lines_val = to_decimal(row['Number of lines'])
                total_value_val = to_decimal(row['Total Value'])
                discrepancy_lines_val = to_decimal(row['Discrepancy Lines'])

                exists = CycleCount.objects.filter(
                    warehouse=row['Warehouse'],
                    number_of_lines=number_of_lines_val,
                    total_value=total_value_val,
                    currency=row['Currency'],
                    created_by=row['Created By'],
                    created_date=row['Created Date'],
                    discrepancy_lines=discrepancy_lines_val,
                    status=row['Status'],
                ).exists()

                if not exists:
                    record = CycleCount.objects.create(
                        cycle_count=cycle_count_val,
                        warehouse=row['Warehouse'],
                        number_of_lines=number_of_lines_val,
                        total_value=total_value_val,
                        currency=row['Currency'],
                        created_by=row['Created By'],
                        created_date=row['Created Date'],
                        discrepancy_lines=discrepancy_lines_val,
                        status=row['Status'],
                        percentage=percentage_val
                    )
                    inserted += 1
                    all_valid.append(record)
                    # break
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
            # Clean row values
            print("roww", row)
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
        
   