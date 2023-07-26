
from . import serializers
from .models import MenuItem,Category
from .models import Order
from rest_framework import generics,viewsets
from rest_framework import permissions,status
from django.contrib.auth.models import User,Group
from rest_framework.decorators import api_view,permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .serializers import MenuItemSerializer,OrderSerializers
# from django.db import transaction
# Create your views here.

#---------------------------custom permission for customer and admin
class CustomAuthentication(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET' and request.user.groups.exists():
            return True
        if request.user.groups.filter(name='Owner').exists():
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='Owner').exists():
            return True
        return False

#------------------------list/delete/post--menu-item-----
class menuItemViewSet(generics.ListCreateAPIView,generics.RetrieveDestroyAPIView):
    # queryset = MenuItem.objects.all()
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = serializers.MenuItemSerializer
    ordering_fields = ['price']
    permission_classes = [CustomAuthentication]


#------------------------list/delete/post--category-item-----
class categoryViewSet(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [CustomAuthentication]



#---------------------------add-to-group-------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_group(request):
    username = request.data['username']
    group = request.data['group']

    #check if user is a admin or manager
    #since mananger can assign only someone to delivery crew
    #and admin can assign anyone to any group
    isadmin = request.user.groups.filter(name='Owner').exists()
    isManager = request.user.groups.filter(name='manager').exists()
    if isManager == True and group != 'delivery_crew':
        return Response({'message':'not authorized'},status.HTTP_401_UNAUTHORIZED)
    
    if isadmin == False:
        return Response({'message':'not authorized'},status.HTTP_401_UNAUTHORIZED)

    if username and group:
        user = get_object_or_404(User,username=username)
        role = get_object_or_404(Group,name=group)
        #below line was earlier added because of no changes in databases
        # with transaction.atomic():
        role.user_set.add(user)
        return Response({'message':'ok'})             
    return Response({'message':'error'}, status.HTTP_400_BAD_REQUEST)

#-------------------------assign user to delivery crew-----


#----------------------------item of the day--------------
@api_view(['GET','POST'])
@permission_classes([permissions.IsAuthenticated])
def item_of_the_day(request,pk=None):
    #if http method is GET then it'll return the item of the day
    if request.method == 'GET':
        item = MenuItem.objects.get(featured=True)
        serialized_data = MenuItemSerializer(item)
        return Response(serialized_data.data)
    
    #if http methd is post then it'll update the item of the day 
    elif request.method == 'POST' and pk:
        #check if authenticated user is manager or not
        if request.user.groups.filter(name='manager').exists():
            #check if given primary key is valid or not
            try:
                item = MenuItem.objects.get(pk=pk)
            except MenuItem.DoesNotExist:
                #in case primary key is not valid it will return http error 404
                return Response({'message':'item not found'},status.HTTP_404_NOT_FOUND)
            
            #in case item was found, then it will be updated to item of the day
            item.featured = True
            item.save()

            #except for current item of the day rest of menu item will have
            #featured attribute equals to false
            MenuItem.objects.exclude(pk=pk).update(featured=False)
            return Response({'message':'item of the day updated'},status.HTTP_200_OK)
        #return 401 response in case of the unauthorized user
        return Response({'message':'only managers are allowed to update the menu'},status.HTTP_401_UNAUTHORIZED)
    
    return Response({'message':'invalid request'},status.HTTP_400_BAD_REQUEST)

#--------------------handle delivery and orders-----------------------
class Order_delivery(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    def list(self,request):
        if request.user.groups.filter(name='delivery_crew').exists():
            orders = Order.objects.filter(delivery_crew=request.user.id)
            serialized_item = OrderSerializers(orders,many=True)
            return Response(serialized_item.data)
        
        #customer's can see their orders with below block of code
        elif request.user.groups.filter(name='customer').exists():
            orders = Order.objects.filter(user=request.user.id)
            serialized_order = OrderSerializers(orders,many=True)
            return Response(serialized_order.data)
        return Response({'message':'user does not exists'},status.HTTP_401_UNAUTHORIZED)
        
    def partial_update(self,request,pk):
        #above is required since there can be cases where 
        #delivery person has multiple delivery and only 
        #finished one the delivery
        if request.user.groups.filter(name='delivery_crew').exists():
            order = get_object_or_404(Order,pk=pk,delivery_crew=request.user.id)
            order.status = True
            order.save()
            return Response({'messege':'Order updated'},status.HTTP_202_ACCEPTED)
        # elif request.user.groups.filter(name='manager').exists():
            
        return Response({'message':'Unauthorized user'},status.HTTP_401_UNAUTHORIZED)
        