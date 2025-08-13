from django.urls import path
from django.contrib.auth import views as auth_views

import main.views as views

password_reset_urls = [
    path('restaurar-contraseña/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name="mailing/password_reset.txt",
        html_email_template_name="mailing/password_reset.html",
        subject_template_name="mailing/password_reset_subject.txt"), name='password_reset'),
    path('restaurar-contraseña/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_sent.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_form.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_done.html'), name='password_reset_complete'),
]

supervisor_urls = [
    path('supervisor/rutas', views.supervisor_scheduled_visits, name="supervisor_scheduled_visits"),
    path('supervisor/nueva-ruta', views.new_schedule_visit, name="new_schedule_visit"),
    path('supervisor/visitas', views.supervisor_visits, name="supervisor_visits"),
    path('supervisor/vendedores', views.supervised_users, name="supervised_users"),
    path('supervisor/asistencias', views.supervisor_attendances, name="supervisor_attendances"),
    path('supervisor/vendedores/<int:id>/progreso', views.supervised_user_progress,
         name="supervised_user_progress"),
    path('supervisor/reportes', views.supervisor_reports, name="supervisor_reports"),
    path('cliente/<int:id>/reporte', views.supervisor_client_sales, name="supervisor_client_sales"),
    path('importar-excel', views.import_excel, name="import_excel"),
]


visits_urls = [
    path('visitas/', views.visits, name="visits"),
    path('visitas/empezar', views.start_visit, name="start_visit"),
    path('rutas', views.scheduled_visits, name="scheduled_visits"),
    path('visitas/<int:id>', views.visit_detail, name="visit_detail"),
    path('visitas/<int:id>/terminar', views.end_visit, name="end_visit"),
    path('visitas/<int:id>/actualizar-comentario', views.update_visit_comment, name="update_visit_comment"),
]

visit_items_urls = [
    path('visitas/<int:id>/agregar-producto', views.add_visit_item, name="add_visit_item"),
    path('visitas/<int:id>/productos/<int:item_id>/editar', views.edit_visit_item, name="edit_visit_item"),
    path('visitas/<int:id>/productos/<int:item_id>/eliminar', views.delete_visit_item, name="delete_visit_item"),
]

clients_urls = [
    path('crear-cliente-y-locacion', views.create_client_and_location, name="create_client_and_location"),
    path('crear-locacion', views.create_location, name="create_location"),
]

attendances_urls = [
    path('asistencias', views.attendances, name="attendances"),
    path('registrar-asistencia', views.start_attendance, name="start_attendance"),
    path('asistencias/<int:id>/terminar', views.end_attendance, name="end_attendance"),
]

urlpatterns = [
                  path('', views.index, name="index"),
                  path('iniciar-sesion', views.sign_in, name="sign_in"),
                  path('cerrar-sesion', auth_views.LogoutView.as_view(), name="logout"),
                  path('progreso', views.progress, name="progress"),
                  path('productos', views.products, name="products"),
                  path('exportar-plantilla', views.export_template, name="export_template"),
              ] + password_reset_urls + visits_urls + visit_items_urls + clients_urls + attendances_urls + supervisor_urls
