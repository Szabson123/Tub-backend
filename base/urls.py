from django.urls import path, include
from rest_framework import routers
from .views import TubViewListSet, ReservationViewSet, RatingViewSet, DiscountViewSet, AddTubView, UserProfileView, UserReservationHistoryView, UserFaqQuestionView, UpdateFaqStatusView, ManagerFaqListView, PublishedFaqListView, FaqUpdateView, SpecificUserProfileView

router = routers.DefaultRouter()
router.register('tubs', TubViewListSet)
router.register('reservations', ReservationViewSet)
router.register('ratings', RatingViewSet)
router.register('discounts', DiscountViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('tubs/<int:pk>/create_reservation/', ReservationViewSet.as_view({'post': 'create_reservation'}), name='create-reservation'),
    path('tubs/<int:pk>/check_reservations/', ReservationViewSet.as_view({'get': 'check_reservations'}), name='check_reservations'),
    path('reservations/', ReservationViewSet.as_view({'get': 'all_reservations'}), name='all_reservations'),
    path('reservations/<int:pk>/accept_reservation/', ReservationViewSet.as_view({'patch': 'accept_reservation'}), name='accept-reservation'),
    path('reservations/<int:pk>/delete_reservation/', ReservationViewSet.as_view({'patch': 'delete_reservation'}), name='delete_reservation'),
    
    path('tubs/<int:pk>/create_rating/', RatingViewSet.as_view({'post':'create_rating'}), name='create_rating'),
    path('tubs/<int:pk>/rating_list/', RatingViewSet.as_view({'get':'rating_list'}), name='rating_list'),
    
    path('add-tub/', AddTubView.as_view(), name='add-tub'),
    
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/reservations/', UserReservationHistoryView.as_view(), name='user-reservation-history'),
    path('profile/<int:user_id>/', SpecificUserProfileView.as_view(), name='specific-user-profile'),

    path('faq/question/', UserFaqQuestionView.as_view(), name='user-faq-question'),
    path('faq/manage/', ManagerFaqListView.as_view(), name='manager-faq-list'),
    path('faq/', PublishedFaqListView.as_view(), name='published-faq-list'),
    path('faq/manage/<int:pk>/status/', UpdateFaqStatusView.as_view(), name='update-faq-status'),
    path('faq/manage/<int:pk>/', FaqUpdateView.as_view(), name='update-faq'),
]
