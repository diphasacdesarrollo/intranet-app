import base64
import uuid
import pandas as pd

from io import BytesIO
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.core.files.base import ContentFile
from django.http import HttpResponse, FileResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from urllib.parse import urlencode
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.timezone import make_naive

from urllib.parse import unquote, quote_plus


@login_required
def index(request):
    template = loader.get_template('index.html')
    context = {
        'today': timezone.now().date()
    }
    return HttpResponse(template.render(context, request))


@require_http_methods(["GET", "POST"])
def sign_in(request):
    next = request.GET.get("next", "/")
    if not request.user.is_authenticated:
        if request.method == "GET":
            template = loader.get_template('accounts/login.html')
            context = {
                'next': next
            }
            return HttpResponse(template.render(context, request))
        elif request.method == "POST":
            username = str(request.POST['username']).lower().replace(" ", "")
            password = request.POST['password']
            user_exists = User.objects.filter(username=username).exists()
            if user_exists:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect(next)
                else:
                    messages.error(request, "Contraseña incorrecta")
            else:
                messages.error(request, "No existe un usuario registrado con el correo " + username + "")
            return redirect(reverse('sign_in') + '?next=' + quote_plus(next))
    else:
        return redirect('index')


@staff_member_required
def export_template(request):
    import io
    import xlsxwriter
    from main.models import Product
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()
    worksheet.write_row(0, 0, data=list(Product.get_column_rename().keys()))
    workbook.close()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="productos" + '.xlsx')


@csrf_exempt
@login_required
def start_visit(request):
    from main.forms import NewVisitForm
    from main.models import Location, Client, get_clients_data
    if request.method == "GET":
        if request.GET.get('selected_location'):
            selected_location = Location.objects.filter(id=request.GET.get('selected_location')).first()
        else:
            selected_location = None

        if request.GET.get('selected_client'):
            selected_client = Client.objects.filter(id=request.GET.get('selected_client')).first()
        else:
            selected_client = None

        template = loader.get_template('start_visit.html')
        context = {
            'locations': Location.objects.all(),
            'form': NewVisitForm(),
            'selected_location': selected_location,
            'selected_client': selected_client,
            'clients_data': get_clients_data()
        }
        return HttpResponse(template.render(context, request))
    elif request.method == "POST":
        form = NewVisitForm(request.POST)
        if form.is_valid():
            visit = form.save()
            visit.check_in = timezone.now()
            visit.save()
            messages.success(request, "Visita iniciada correctamente")
            return redirect('visit_detail', id=visit.id)
        else:
            messages.error(request, "Error al iniciar visita")
            return redirect('start_visit')


@login_required
def end_visit(request, id):
    from main.models import Visit
    visit = Visit.objects.get(id=id)
    visit.check_out = timezone.now()
    visit.save()
    messages.success(request, "Visita finalizada correctamente")
    return redirect('visit_detail', id=id)


@login_required
def supervisor_visits(request):
    from main.models import Visit, SupervisedUser

    # Supervised user filter
    supervised_user_filter = request.GET.get('supervised_user_filter')

    # Date filters
    from_date = request.GET.get('from_date', timezone.now().date())
    to_date = request.GET.get('to_date', timezone.now().date())

    # Get supervised users
    supervised_users = request.user.supervised_users.all()
    users = User.objects.filter(id__in=[su.supervised_user.id for su in supervised_users])

    # Get visits
    visits = Visit.objects.filter(check_in__date__gte=from_date,
                                  check_in__date__lte=to_date).order_by('-check_in')

    if supervised_user_filter is not None and supervised_user_filter != '':
        visits = visits.filter(user__id=supervised_user_filter)
    else:
        visits = visits.filter(user__in=users)

    paginator = Paginator(visits, 20)
    page_number = request.GET.get('page', 1)
    visits = paginator.get_page(page_number)
    template = loader.get_template('supervisor/visits.html')
    context = {
        'visits': visits,
        'from_date': from_date,
        'to_date': to_date,
        'supervised_users': users,
        'supervised_user_filter': supervised_user_filter
    }
    return HttpResponse(template.render(context, request))


@login_required
def visits(request):
    from main.models import Visit
    filter_date = request.GET.get('filter_date', timezone.now().date())
    visits = Visit.objects.filter(check_in__date=filter_date, user=request.user).order_by('-check_in')
    template = loader.get_template('visits.html')
    context = {
        'visits': visits,
        'filter_date': filter_date
    }
    return HttpResponse(template.render(context, request))


@login_required
def visit_detail(request, id):
    from main.models import Visit, Product, Distributor
    visit = Visit.objects.get(id=id)
    template = loader.get_template('visit_detail.html')
    context = {
        'now': timezone.now(),
        'visit': visit,
        'items': visit.items.all(),
        'products': Product.objects.all(),
        'distributors': Distributor.objects.all().order_by('name'),
        'can_edit': True,
    }
    return HttpResponse(template.render(context, request))


@login_required
@csrf_exempt
@require_POST
def add_visit_item(request, id):
    from main.models import Visit
    visit = Visit.objects.get(id=id)
    from main.forms import NewVisitItemForm
    if request.method == "POST":
        form = NewVisitItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto agregado correctamente")
        else:
            messages.error(request, "Error al agregar producto. " + str(form.errors))
        return redirect('visit_detail', id=id)


def delete_visit_item(request, id, item_id):
    from main.models import VisitItem
    VisitItem.objects.get(id=item_id).delete()
    messages.success(request, "Producto eliminado correctamente")
    return redirect('visit_detail', id=id)


@csrf_exempt
@require_POST
@login_required
def edit_visit_item(request, id, item_id):
    from main.models import VisitItem
    from main.forms import EditVisitItemForm
    visit_item = VisitItem.objects.get(id=item_id)
    form = EditVisitItemForm(request.POST, instance=visit_item)
    if form.is_valid():
        form.save()
        messages.success(request, "Producto editado correctamente")
    else:
        messages.error(request, "Error al editar producto. " + str(form.errors))
    return redirect('visit_detail', id=id)


@login_required
def scheduled_visits(request):
    from main.models import ScheduledVisit
    filter_date = request.GET.get('filter_date', timezone.now().date())
    scheduled_visits = ScheduledVisit.objects.filter(check_in=filter_date, user=request.user).order_by('-check_in')
    template = loader.get_template('scheduled_visits.html')
    context = {
        'title': "Rutas",
        'scheduled_visits': scheduled_visits,
        'filter_date': filter_date
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required
def new_schedule_visit(request):
    from main.forms import NewScheduleVisitForm
    from main.models import Location, Client, get_clients_data
    if request.method == "GET":
        if request.GET.get('selected_location'):
            selected_location = Location.objects.filter(id=request.GET.get('selected_location')).first()
        else:
            selected_location = None

        if request.GET.get('selected_client'):
            selected_client = Client.objects.filter(id=request.GET.get('selected_client')).first()
        else:
            selected_client = None

        supervised_users = request.user.supervised_users.all()
        users = User.objects.filter(id__in=[su.supervised_user.id for su in supervised_users])

        template = loader.get_template('supervisor/new_scheduled_visit.html')
        context = {
            'locations': Location.objects.all(),
            'selected_location': selected_location,
            'selected_client': selected_client,
            'clients_data': get_clients_data(),
            'supervised_users': users,
        }
        return HttpResponse(template.render(context, request))
    elif request.method == "POST":
        form = NewScheduleVisitForm(request.POST)
        if form.is_valid():
            try:
                scheduled_visit = form.save()
            except Exception as e:
                messages.error(request, "Error al iniciar visita programada " + str(e))
                return redirect('new_schedule_visit')
            else:
                messages.success(request, "Nueva ruta agregada")
                return redirect('supervisor_scheduled_visits')
        else:
            messages.error(request, "Error al agregar nueva ruta. " + str(form.errors))
            return redirect('new_schedule_visit')


def edit_schedule_visit(request, id):
    from main.models import ScheduledVisit
    from main.forms import EditScheduleVisitForm
    schedule_visit = ScheduledVisit.objects.get(id=id)
    schedule_visit_form = EditScheduleVisitForm(request.POST, instance=schedule_visit)
    if schedule_visit_form.is_valid():
        try:
            schedule_visit_form.save()
        except Exception as e:
            messages.error(request, "Error al editar visita programada " + str(e))
        else:
            messages.success(request, "Visita programada editada correctamente")
    else:
        messages.error(request, "Error al editar visita programada " + str(schedule_visit_form.errors))
    url = reverse('supervisor_scheduled_visits')
    query_params = {'foo': 'bar'}
    return redirect(f"{url}?{urlencode(query_params)}")


def remove_schedule_visit(request, id):
    from main.models import ScheduledVisit
    try:
        ScheduledVisit.objects.get(id=id).delete()
    except Exception as e:
        messages.error(request, "Error al eliminar visita programada " + str(e))
    else:
        messages.success(request, "Visita programada eliminada correctamente")
    return redirect('supervisor_scheduled_visits')


def create_client_and_location(request):
    from main.forms import NewClientForm, NewLocationForm
    from main.models import Client, Location
    client_form = NewClientForm(request.POST)
    location_form = NewLocationForm(request.POST)
    # First create client
    if client_form.is_valid():
        try:
            client = client_form.save()
        except Exception as e:
            messages.error(request, "Error al crear cliente " + str(e))
        else:
            # Add client id to location form
            location_form.data = location_form.data.copy()
            location_form.data['client'] = client.id
            # Then create location
            if location_form.is_valid():
                location = location_form.save(commit=False)
                location.client = client
                location.save()
                messages.success(request, "Cliente y local creados correctamente")
                return redirect(f"{reverse('start_visit')}?selected_location={location.id}&selected_client={client.id}")
            else:
                messages.error(request, "El cliente fue creado pero hubo un error al crear el local del cliente " + str(
                    location_form.errors))
                return redirect(f"{reverse('start_visit')}?selected_client={client.id}")
    else:
        messages.error(request, "Error al crear cliente " + str(client_form.errors))
    return redirect('start_visit')


def update_visit_comment(request, id):
    from main.models import Visit
    from main.forms import VisitCommentForm
    visit = Visit.objects.get(id=id)
    visit_comment_form = VisitCommentForm(request.POST, instance=visit)
    if visit_comment_form.is_valid():
        visit_comment_form.save()
        messages.success(request, "Comentario actualizado correctamente")
    else:
        messages.error(request, "No se pudo actualizar el comentario")
    return redirect('visit_detail', id=id)


def import_excel(request):
    if request.method == "GET":
        template = loader.get_template('supervisor/import_excel.html')
        context = {
        }
        return HttpResponse(template.render(context, request))
    elif request.method == "POST":
        from main.models import SupervisedUser
        from main.forms import ImportExcelForm
        form = ImportExcelForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                success_count, error_rows = SupervisedUser.import_from_excel(form.cleaned_data["file"])
            except Exception as e:
                messages.error(request, str(e))
            else:
                message = f"Filas importadas correctamente: {success_count}"
                if error_rows:
                    message += f". Filas con errores: {error_rows}"
                messages.success(request, message)
            return redirect('import_excel')
        else:
            messages.error(request, str(form.errors))
            return redirect('import_excel')


def create_location(request):
    from main.forms import NewLocationForm
    location_form = NewLocationForm(request.POST)
    # First create client
    if location_form.is_valid():
        location = location_form.save()
        messages.success(request, "Local creado correctamente")
        return redirect(f"{reverse('start_visit')}?selected_location={location.id}&selected_client={location.client.id}")
    else:
        messages.error(request, "No se pudo crear la ubicación" + str(
            location_form.errors))
        return redirect(f"{reverse('start_visit')}")

    return redirect('start_visit')


def importar(request):
    if request.method == "GET":
        template = loader.get_template('importar.html')
        context = {
        }
        return HttpResponse(template.render(context, request))
    elif request.method == "POST":
        from main.models import Product
        from main.forms import ImportForm
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                Product.import_from_excel(form.cleaned_data["file"])
                messages.success(request, "Productos importados correctamente")
            except Exception as e:
                messages.error(request, str(e))
            return redirect('importar')
        else:
            messages.error(request, str(form.errors))
            return redirect('importar')



"""Attendance views"""
def attendances(request):
    from main.models import Attendance
    from main.services import SPANISH_MONTHS
    month_filter = request.GET.get('month_filter', timezone.now().month)
    year_filter = request.GET.get('year_filter', timezone.now().year)
    attendances = Attendance.objects.all().filter(user=request.user,
                                                  check_in__month=month_filter,
                                                  check_in__year=year_filter).order_by('-check_in')
    template = loader.get_template('attendances.html')
    context = {
        'months': SPANISH_MONTHS,
        'month_filter': month_filter,
        'year_filter': year_filter,
        'attendances': attendances
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
def start_attendance(request):
    from main.forms import StartAttendanceForm
    if request.method == "GET":
        # First validate there are no assistances started without end
        from main.models import Attendance
        if Attendance.objects.filter(user=request.user, check_out__isnull=True).exists():
            messages.error(request, "Tienes una asistencia registrada sin hora de fin. Por favor finaliza la asistencia antes de iniciar una nueva.")
            return redirect('attendances')
        template = loader.get_template('start_attendance.html')
        context = {
            'form': StartAttendanceForm(),
        }
        return HttpResponse(template.render(context, request))
    elif request.method == "POST":
        photo_data = request.POST.get('check_in_photo')  # Get base64 image string

        if photo_data and "data:image" in photo_data:
            # Extract base64 data (removing prefix like "data:image/jpeg;base64,")
            format, imgstr = photo_data.split(';base64,')
            ext = format.split('/')[-1]  # Get image extension (jpg, png, etc.)

            # Decode the base64 string
            image_data = base64.b64decode(imgstr)
            image_name = f"check_in_{uuid.uuid4()}.{ext}"

            # Create a ContentFile and add it to request.FILES
            request.FILES['check_in_photo'] = ContentFile(image_data, name=image_name)
        print("request.POST")
        print(request.POST)
        print("request.FILES")
        print(request.FILES)
        # Initialize form with updated request.FILES
        form = StartAttendanceForm(request.POST, request.FILES)
        if form.is_valid():
            print("check in photo")
            attendance = form.save()
            attendance.check_in = timezone.now()
            attendance.user = request.user
            attendance.save()
            messages.success(request, "Asistencia iniciada correctamente")
            return redirect('attendances')
        else:
            messages.error(request, "Error al registrar asistencia")
            return redirect('start_attendance')


@require_POST
def end_attendance(request, id):
    from main.models import Attendance
    from main.forms import EndAttendanceForm
    attendance = Attendance.objects.get(id=id)
    form = EndAttendanceForm(request.POST, instance=attendance)
    if form.is_valid():
        attendance = form.save()
        attendance.check_out = timezone.now()
        attendance.save()
        messages.success(request, "Asistencia finalizada correctamente")
        return redirect('attendances')
    else:
        messages.error(request, "Error al registrar fin de asistencia")
        return redirect('attendances')


"""Progress views"""
@login_required
def progress(request):
    from main.models import get_progress, ProductPrice
    date = request.GET.get('date', timezone.now().date())
    context = {
        'product_prices': get_progress(request.user, date),
        'monthly_product_prices': ProductPrice.get_monthly_product_prices(date)
    }
    template = loader.get_template('progress.html')
    return HttpResponse(template.render(context, request))


@login_required
def supervised_users(request):
    from django.contrib.auth.models import User
    template = loader.get_template('supervisor/supervised_users.html')
    supervised_users = request.user.supervised_users.all()
    users = User.objects.filter(id__in=[su.supervised_user.id for su in supervised_users])
    context = {
        'supervised_users': users
    }
    return HttpResponse(template.render(context, request))


@login_required
def supervised_user_progress(request, id):
    from main.models import get_progress
    user = User.objects.get(id=id)
    date = request.GET.get('date', timezone.now().date())
    context = {
        'user': user,
        'product_prices': get_progress(user, date)
    }
    template = loader.get_template('supervisor/supervised_user_progress.html')
    return HttpResponse(template.render(context, request))


def supervisor_attendances(request):
    from main.models import Attendance

    # Supervised user filter
    supervised_user_filter = request.GET.get('supervised_user_filter')

    # Date filters
    from_date = request.GET.get('from_date', timezone.now().replace(day=1).date())
    to_date = request.GET.get('to_date', timezone.now().date())

    # Get supervised users
    supervised_users = request.user.supervised_users.all()
    users = User.objects.filter(id__in=[su.supervised_user.id for su in supervised_users])

    # Get attendances
    attendances = Attendance.objects.filter(check_in__date__gte=from_date,
                                            check_in__date__lte=to_date).order_by('-check_in')

    if supervised_user_filter is not None and supervised_user_filter != '':
        attendances = attendances.filter(user__id=supervised_user_filter)
    else:
        attendances = attendances.filter(user__in=users).order_by('-check_in')

    paginator = Paginator(attendances, 10)
    page_num = request.GET.get('pagina', 1)
    attendances = paginator.get_page(page_num)

    context = {
        'visits': visits,
        'from_date': from_date,
        'to_date': to_date,
        'supervised_users': users,
        'supervised_user_filter': supervised_user_filter,
        'attendances': attendances,
        'today': timezone.now().date(),
        'paginator': paginator
    }
    template = loader.get_template('supervisor/attendances.html')
    return HttpResponse(template.render(context, request))


@login_required
def products(request):
    from main.models import Product
    products = Product.objects.all().filter(show_on_catalog=True)
    categories = Product.CategoryChoices.choices
    category_filter = request.GET.get('category_filter')
    if category_filter != '' and category_filter is not None:
        products = products.filter(category=category_filter)
    template = loader.get_template('products.html')
    context = {
        'products': products.order_by('name'),
        'categories': categories,
        'category_filter': category_filter
    }
    return HttpResponse(template.render(context, request))


@login_required
def supervisor_scheduled_visits(request):
    from main.models import ScheduledVisit, SupervisedUser

    # Supervised user filter
    supervised_user_filter = request.GET.get('supervised_user_filter')

    # Date filters
    from_date = request.GET.get('from_date', timezone.now().date())
    to_date = request.GET.get('to_date', timezone.now().date())

    # Get supervised users
    supervised_users = request.user.supervised_users.all()
    users = User.objects.filter(id__in=[su.supervised_user.id for su in supervised_users])

    # Get visits
    scheduled_visits = ScheduledVisit.objects.filter(check_in__gte=from_date,
                                                     check_in__lte=to_date).order_by('-check_in')

    if supervised_user_filter is not None and supervised_user_filter != '':
        scheduled_visits = scheduled_visits.filter(user__id=supervised_user_filter)
    else:
        scheduled_visits = scheduled_visits.filter(user__in=users)

    paginator = Paginator(scheduled_visits, 20)
    page_number = request.GET.get('page', 1)
    scheduled_visits = paginator.get_page(page_number)
    template = loader.get_template('supervisor/scheduled_visits.html')
    context = {
        'scheduled_visits': scheduled_visits,
        'from_date': from_date,
        'to_date': to_date,
        'supervised_users': users,
        'supervised_user_filter': supervised_user_filter
    }
    return HttpResponse(template.render(context, request))

def supervisor_reports(request):
    from main.models import VisitItem, Client, Product
    from collections import defaultdict
    # Date filters
    from_date = request.GET.get('from_date', timezone.now().replace(day=1).date())
    if type(from_date) is str:
        from_date = timezone.datetime.strptime(from_date, "%Y-%m-%d").date()
    from_datetime = timezone.datetime.combine(from_date, timezone.datetime.min.time())
    to_date = request.GET.get('to_date', timezone.now().date())
    if type(to_date) is str:
        to_date = timezone.datetime.strptime(to_date, "%Y-%m-%d").date()
    to_datetime = timezone.datetime.combine(to_date, timezone.datetime.max.time())

    # Sellers
    supervised_users = request.user.supervised_users.all()
    users = User.objects.filter(id__in=[su.supervised_user.id for su in supervised_users])

    # Query the VisitItem table for the given date and fetch related objects efficiently
    visit_items = VisitItem.objects.filter(
        visit__check_in__gte=from_datetime, visit__check_in__lte=to_datetime, visit__user__in=users
    ).select_related('visit', 'product', 'visit__location__client')

    # Get unique clients queryset from visits_items, get a queryset of clients. very efficient
    clients = Client.objects.filter(id__in=visit_items.values_list('visit__location__client', flat=True)).order_by('name')

    # Client filter
    client_filter = request.GET.get('client_filter')
    if client_filter is not None and client_filter != '':
        client_filter = Client.objects.get(id=client_filter)
        visit_items = visit_items.filter(visit__location__client__name=client_filter)

    # Dictionary to store product counts per client
    data = defaultdict(lambda: defaultdict(int))
    products = set()
    clients_columns = set()

    for item in visit_items:
        product_name = item.product.name if item.product else "Unknown Product"
        client_name = item.visit.location.client.name if item.visit.location and item.visit.location.client else "Unknown Client"

        products.add(product_name)
        clients_columns.add(client_name)
        data[product_name][client_name] += item.quantity

    # Sort product and client lists
    products = sorted(products)
    clients_columns = sorted(clients_columns)

    clients_ids = {}
    for client in clients:
        clients_ids[client.name] = client.id

    products_ids = {}
    for product in Product.objects.all():
        products_ids[product.name] = product.id

    context = {
        "products": products,
        "clients_columns": clients_columns,
        "data": data,
        "from_date": from_date,
        "to_date": to_date,
        "client_filter": client_filter,
        "clients": clients,
        "clients_ids": clients_ids,
        "products_ids": products_ids,
    }
    template = loader.get_template('supervisor/reports.html')
    return HttpResponse(template.render(context, request))


def supervisor_client_sales(request, id):
    from main.models import Client, VisitItem, Product
    from django.db.models import F, ExpressionWrapper, DecimalField, Sum

    client = Client.objects.get(id=id)

    # From date filter
    from_date = request.GET.get('from_date', timezone.now().replace(day=1).date())
    if type(from_date) is str:
        from_date = timezone.datetime.strptime(from_date, "%Y-%m-%d").date()
    from_datetime = timezone.datetime.combine(from_date, timezone.datetime.min.time())

    # To date filter
    to_date = request.GET.get('to_date', timezone.now().date())
    if type(to_date) is str:
        to_date = timezone.datetime.strptime(to_date, "%Y-%m-%d").date()
    to_datetime = timezone.datetime.combine(to_date, timezone.datetime.max.time())

    products = Product.objects.all().order_by('name')

    # product filter
    product_filter = request.GET.get('product_filter')

    visit_items = VisitItem.objects.filter(
        visit__check_in__gte=from_datetime, visit__check_in__lte=to_datetime, visit__location__client=client
    ).select_related('visit', 'product')
    if product_filter is not None and product_filter != "":
        product_filter = Product.objects.get(id=product_filter)
        visit_items = visit_items.filter(product=product_filter)
    else:
        visit_items = visit_items.order_by('product__name')

    # Having visit items, multiply the quantity by the price for each item and them sum all
    total_sales = visit_items.aggregate(
        total=Sum(F('quantity') * F('unit_price'))
    )['total'] or 0

    export = request.GET.get("export")
    if export is not None and export != "":
        if export == "xlsx":
            file_headers = VisitItem.export_headers()
            inflows_values = visit_items.values(
                "visit__check_in__date", "product__name", "product__presentation", "quantity", "unit_price",
                "distributor__name", "visit__user__email"
            )

            # Convert the QuerySet to a DataFrame directly
            df = pd.DataFrame.from_records(inflows_values)

            # Convert timezone-aware datetimes to timezone-unaware datetimes
            for datetime_field in ['archived_at', 'created_at', 'updated_at']:
                if datetime_field in df.columns:
                    df[datetime_field] = df[datetime_field].apply(
                        lambda x: make_naive(x) if pd.notnull(x) and not timezone.is_naive(x) else x
                    )

            # Get the current datetime and format it
            current_datetime = timezone.now().strftime('%Y-%m-%d_%H-%M-%S')

            # Create the filename with the datetime
            filename = f"ventas_{current_datetime}.xlsx"

            # Export to Excel
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={filename}'
            df.to_excel(response, index=False, header=file_headers)

            return response

    paginator = Paginator(visit_items, 100)
    page_num = request.GET.get('pagina', 1)
    visit_items = paginator.get_page(page_num)

    context = {
        "client": client,
        "products": products,
        "visit_items": visit_items,
        "from_date": from_date,
        "to_date": to_date,
        "product_filter": product_filter,
        "paginator": paginator,
        "total": total_sales,
    }
    template = loader.get_template('supervisor/client_sales.html')
    return HttpResponse(template.render(context, request))