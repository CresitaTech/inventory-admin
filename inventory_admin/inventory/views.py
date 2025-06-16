from django.shortcuts import render

# Create your views here.
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OnHandBalanceReport
from .serializers import OnHandBalanceReportSerializer
from io import BytesIO

class OnHandBalanceReportView(APIView):
    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file)
        except Exception as e:
            return Response({'error': f'Failed to read Excel file. {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
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