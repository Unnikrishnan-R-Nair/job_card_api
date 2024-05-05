from django.shortcuts import render

from rest_framework.generics import CreateAPIView,ListAPIView,UpdateAPIView,DestroyAPIView,RetrieveAPIView

from rest_framework.response import Response

from rest_framework import status

from rest_framework import authentication, permissions

from .serializers import UserSerializer, AdvisorSerializer, JobCardSerializer, JobSerializer, JobSummarySerializer, AdminSerializer

from django.contrib.auth.models import User

from . models import JobCard, Job

from . permissions import IsOwnerOrAdmin

from django.db.models import Sum



class AdminView(CreateAPIView):

    serializer_class=AdminSerializer

    queryset=User.objects.all()



class ServiceAdvisorView(CreateAPIView, ListAPIView):

    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAdminUser]

    serializer_class=UserSerializer

    queryset=User.objects.all()

    def get_queryset(self):
        return User.objects.exclude(is_staff=True)

class ServiceAdvisorManageView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):

    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAdminUser]

    serializer_class=AdvisorSerializer

    queryset=User.objects.all()


    def delete(self, request, *args, **kwargs):

        user_object = User.objects.get(id=kwargs.get("pk"))

        # print(user_object)

        user_object.is_active=False

        user_object.save()

        return Response(data={"message": "Advisor account deactivated."})



class JobCardView(CreateAPIView, ListAPIView):

    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAuthenticated]

    serializer_class=JobCardSerializer

    queryset=JobCard.objects.all()

    def list(self, request, *args, **kwargs):
        if request.user.is_active:
            return super().list(request, *args, **kwargs)
        else:
            return Response(data={"message":"Account deactivated. Contact admin"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    
    def create(self, request, *args, **kwargs):
        if request.user.is_active:
            return super().create(request, *args, **kwargs)
        else:
            return Response(data={"message":"Account deactivated. Contact admin"}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def perform_create(self, serializer):

        serializer.save(advisor=self.request.user)


class JobCardManageView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):

    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAuthenticated]

    serializer_class=JobCardSerializer

    queryset=JobCard.objects.all()

    def retrieve(self, request, *args, **kwargs):
        job_card_obj = JobCard.objects.get(id=kwargs.get("pk"))
        if job_card_obj.is_active:
            return super().retrieve(request, *args, **kwargs)
        else:
            return Response(data={"message":"Jobcard cancelled. Contact admin."}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def update(self, request, *args, **kwargs):
        job_card_obj = JobCard.objects.get(id=kwargs.get("pk"))
        if request.user.is_staff:
            return super().update(request, *args, **kwargs)
        elif job_card_obj.is_active:
            if request.data.status == "Cancelled":
                job_card_obj.status="Cancelled"
                job_card_obj.is_active=False
                job_card_obj.save()
            return super().update(request, *args, **kwargs)
        else:
            return Response(data={"message":"Jobcard cancelled. Contact admin for re-opening the card"}, status=status.HTTP_406_NOT_ACCEPTABLE)


    def delete(self, request, *args, **kwargs):
        if request.user.is_active:
            job_card_obj = JobCard.objects.get(id=kwargs.get("pk"))
            job_card_obj.status="Cancelled"
            job_card_obj.is_active=False
            job_card_obj.save()
            return Response(data={"message":"Jobcard cancelled"})
        else:
            return Response(data={"message":"Account deactivated. Contact admin"}, status=status.HTTP_406_NOT_ACCEPTABLE)


class JobView(CreateAPIView, ListAPIView):

    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAuthenticated, IsOwnerOrAdmin]

    serializer_class=JobSerializer

    queryset=Job.objects.all()

    def list(self, request, *args, **kwargs):
        
        job_card_obj = JobCard.objects.get(id=kwargs.get("pk"))

        if job_card_obj.advisor == request.user:

            return super().list(request, *args, **kwargs)
        else:

            return Response(data={"message":"Not allowed"}, status=status.HTTP_401_UNAUTHORIZED)
       

    def create(self, request, *args, **kwargs):
        try:
            job_card_obj=JobCard.objects.get(id=kwargs.get("pk"))
        except:
            return Response(data={"message":"No jobcard found"},status=status.HTTP_404_NOT_FOUND)

        if job_card_obj.advisor == request.user:

            serializer_instance = JobSerializer(data=request.data)

            if serializer_instance.is_valid():

                serializer_instance.save(advisor=request.user, job_card_object=job_card_obj)

                return Response(data=serializer_instance.data, status=status.HTTP_201_CREATED)
            
            return Response(data=serializer_instance.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data={"message":"Not allowed"}, status=status.HTTP_401_UNAUTHORIZED)
        
  

class JobManageView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):

    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAuthenticated, IsOwnerOrAdmin]

    serializer_class=JobSerializer

    queryset=Job.objects.all()



class JobCardSummaryView(RetrieveAPIView):
    
    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAuthenticated, IsOwnerOrAdmin]

    serializer_class=JobCardSerializer

    queryset=JobCard.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            job_card_obj = JobCard.objects.get(id=kwargs.get("pk"))
        except:
            return Response(data={"message": "No jobcard found"}, status=status.HTTP_404_NOT_FOUND)
        
        jobs_obj = Job.objects.filter(job_card_object=job_card_obj)

        amt = jobs_obj.values('amount').aggregate(total=Sum('amount'))
        print(amt)

        serializer_instance = JobSummarySerializer(jobs_obj, many=True)

        # estimate_amount=0
        # for i in serializer_instance.data:
        #     # print(i["amount"])
        #     estimate_amount+=i["amount"]
        
        # print(estimate_amount)

        estimate_amount = amt.get('total') or 0
        
        data = {
            "id":job_card_obj.id,
            "advisor": job_card_obj.advisor.username,
            "customer": job_card_obj.customer_name,
            "vehicle number":job_card_obj.vehicle_num,
            "kilometer reading": job_card_obj.kilometers,
            "phone": job_card_obj.phone,
            "email": job_card_obj.email,
            "status": job_card_obj.status,
            "job": serializer_instance.data,
            "estimate_amount": estimate_amount,
            "remark": job_card_obj.remark,
            "created_date": job_card_obj.created_date,
            "updated_date": job_card_obj.updated_date, 
        }

        return Response(data=data)