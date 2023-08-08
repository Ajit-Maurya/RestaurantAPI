from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path('menu-items/',views.menu_item),
    path('menu-items',views.menuItemViewSet.as_view()),
    path('menu-items/<int:pk>',views.menuItemViewSet.as_view()),
    path('category',views.categoryViewSet.as_view()),
    path('api-token-auth',obtain_auth_token),
    path('add-to-group',views.assign_group),
    path('item-of-the-day',views.item_of_the_day),
    path('item-of-the-day/<int:pk>',views.item_of_the_day),
    path('order_and_delivery',views.Order_delivery.as_view({'get':'list'})),
    path('order_and_delivery/<int:pk>',views.Order_delivery.as_view({'patch':'partial_update'})),
    path('cart',views.Cart_API.as_view({'get':'list','post':'create'})),
    path('place-order',views.place_order),
    # path('category/<int:pk>/',views.category_detail,name='category-detail'),
]