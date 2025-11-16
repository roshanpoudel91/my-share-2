from django.urls import path, include
from . import views

app_name='finapp'

urlpatterns = [
    path('', views.mainview, name='main_view'),
    #path('stockdata/',views.StockInputView.as_view(), name='stock_input'),
    path('stock/',views.StockSelectionView.as_view(), name='stock_selection'),
    path('realestate/',views.RealEstateView.as_view(), name='real_estate'),
    path('contact/',views.ContactView.as_view(),name='contact'),
    path('extra/',views.ExtraView.as_view(),name='extra'),
    path('privacy/',views.privacy, name='privacy'),
    path('termsofuse/',views.termsofuse, name='termsofuse'),

    path('stock2/', views.StockSelection2View.as_view(), name='stock_selection2'), #This one is for new autocomplete feature.
    path('coming/', views.coming, name="coming"),
    path('plans/', views.plans, name='plans'),
    path('help/',views.helps,name='help'),
    path('temp-upload/',views.temp,name='temp'),
    path('performance-tab/',views.stockPerformaceTab,name='stockPerformaceTab'),
    path('visual-tab/',views.stockVisualTab,name='stockVisualTab'),
    path('backTest-tab/',views.stockBackTestTab,name='stockBackTestTab'),

    #======= BETA PAGE ===============
    path('betastock/',views.BetaStockSelectionView.as_view(), name='beta_stock_selection'),
    #=================END BETA PAGE =======

    ]
