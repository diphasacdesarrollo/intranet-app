from django import forms

from main.models import Visit, VisitItem, Client, Location, Attendance, ScheduledVisit


class ImportForm(forms.Form):
    file = forms.FileField(required=True)


class NewVisitForm(forms.ModelForm):

    class Meta:
        model = Visit
        fields = ('check_in', 'latitude', 'longitude', 'user', 'location', 'comment')
        widgets = {
            'user': forms.HiddenInput()
        }


class NewVisitItemForm(forms.ModelForm):

    class Meta:
        model  = VisitItem
        fields = ('visit', 'product', 'unit_price', 'distributor', 'quantity')


class EditVisitItemForm(forms.ModelForm):

    class Meta:
        model = VisitItem
        fields = ('quantity', 'product', 'unit_price', 'distributor')


class NewClientForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ('ruc', 'name')


class NewLocationForm(forms.ModelForm):

    class Meta:
        model = Location
        fields = ('latitude', 'longitude', 'address', 'googlemaps_place_id', 'client')


class StartAttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance
        fields = ('user', 'check_in', 'latitude_check_in', 'longitude_check_in', 'check_in_photo')


class NewScheduleVisitForm(forms.ModelForm):

    class Meta:
        model = ScheduledVisit
        fields = ('check_in', 'user', 'supervisor', 'location', 'comment')


class EditScheduleVisitForm(forms.ModelForm):

    class Meta:
        model = ScheduledVisit
        fields = ('check_in', 'user', 'location', 'comment')


class EndAttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance
        fields = ('check_out', 'latitude_check_out', 'longitude_check_out', 'check_out_photo')


class VisitCommentForm(forms.ModelForm):

    class Meta:
        model = Visit
        fields = ('comment',)


class ImportExcelForm(forms.Form):
    file = forms.FileField(required=True)
    type = forms.ChoiceField(choices=[('validate', 'validate'), ('import', 'import')], required=True)
