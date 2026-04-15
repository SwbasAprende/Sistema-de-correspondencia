from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('radicados/', views.lista_radicados, name='lista'),
    path('nuevo/', views.crear_radicado, name='crear'),
    path('<int:pk>/', views.detalle_radicado, name='detalle'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado, name='cambiar_estado'),
    path('<int:pk>/barcode/', views.barcode_image, name='barcode_image'),
    path('<int:pk>/imprimir/', views.imprimir_sticker, name='imprimir_sticker'),
    path('exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('ayuda/', views.ayuda, name='ayuda'),
]