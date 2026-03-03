import io
import os
from django.db.models import Sum, F
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from ..models import Goods, Stocks, Goodincomes, Goodmoves, Goodsales

class GoodRestView(APIView):
    permission_classes = [IsAuthenticated]

    def get_balances(self, request, wnameStock, wnameGood):
        if not hasattr(request.user, 'profile'): return []
        tenant = request.user.profile.tenant
        balances = {}
        inc = Goodincomes.objects.filter(stock__tenant=tenant).values(s=F('stock__nameStock'), g=F('good__nameGood')).annotate(t=Sum('qty'))
        for r in inc: balances[(r['s'], r['g'])] = balances.get((r['s'], r['g']), 0) + r['t']
        m_from = Goodmoves.objects.filter(stockFrom__tenant=tenant).values(s=F('stockFrom__nameStock'), g=F('good__nameGood')).annotate(t=Sum('qty'))
        for r in m_from: balances[(r['s'], r['g'])] = balances.get((r['s'], r['g']), 0) - r['t']
        m_to = Goodmoves.objects.filter(stockTo__tenant=tenant).values(s=F('stockTo__nameStock'), g=F('good__nameGood')).annotate(t=Sum('qty'))
        for r in m_to: balances[(r['s'], r['g'])] = balances.get((r['s'], r['g']), 0) + r['t']
        sales = Goodsales.objects.filter(stock__tenant=tenant).values(s=F('stock__nameStock'), g=F('good__nameGood')).annotate(t=Sum('qty'))
        for r in sales: balances[(r['s'], r['g'])] = balances.get((r['s'], r['g']), 0) - r['t']
        res = [{"nameStock": k[0], "nameGood": k[1], "qty": v} for k, v in balances.items()]
        if wnameStock != "All": res = [r for r in res if r['nameStock'] == wnameStock]
        if wnameGood != "All": res = [r for r in res if r['nameGood'] == wnameGood]
        return sorted(res, key=lambda x: (x['nameStock'], x['nameGood']))

    def get(self, request, wnameStock="All", wnameGood="All"):
        return Response(self.get_balances(request, wnameStock, wnameGood))

    def post(self, request, wnameStock="All", wnameGood="All"):
        data = self.get_balances(request, wnameStock, wnameGood)
        buffer = io.BytesIO()
        f_name = "Helvetica"
        paths = ["C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
        for p in paths:
            if os.path.exists(p):
                try:
                    pdfmetrics.registerFont(TTFont('RusFont', p))
                    f_name = 'RusFont'
                    break
                except: continue
        
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.fontName = f_name
        
        tenant_name = request.user.profile.tenant.name if hasattr(request.user, 'profile') else "Sklad PRO"
        elements.append(Paragraph(f"Отчет компании: {tenant_name}", title_style))
        
        table_data = [["Склад", "Товар", "Остаток"]]
        for item in data:
            table_data.append([item['nameStock'], item['nameGood'], str(item['qty'])])
            
        t = Table(table_data, colWidths=[180, 180, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, -1), f_name),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='Report.pdf')

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        tenant = request.user.profile.tenant
        return Response({"cards": {"goods": Goods.objects.filter(tenant=tenant).count(), "stocks": Stocks.objects.filter(tenant=tenant).count(), "operations": Goodincomes.objects.filter(stock__tenant=tenant).count()}})

class AIAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        return Response({"report": "ИИ: Оптимизируйте закупки."})
