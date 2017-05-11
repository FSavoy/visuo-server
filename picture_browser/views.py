from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from forms import SkyPictureQueryForm
from data.models import SkyPicture, MeasuringDevice
from django.template.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def index(request, page=1):
    """
    Generates the picture browsing page, consisting of the list of pictures and the selection form (created with a custom form SkyPictureQueryForm)
    """
    
    args = {}
    args.update(csrf((request)))
    
    # Get already stored or submitted search values
    if request.POST or 'POST' in request.session:
        if request.POST:
            form_values = request.POST
            request.session['POST'] = form_values
        else:
            form_values = request.session['POST']
        form_search = SkyPictureQueryForm(form_values)
    else:
        form_search = SkyPictureQueryForm()
        toShow = SkyPicture.objects.all().order_by('-date','-time')
    
    # Retrieving the data
    if form_search.is_valid():
        start_date = form_search.cleaned_data['start_date']
        end_date = form_search.cleaned_data['end_date']
        start_time = form_search.cleaned_data['start_time']
        end_time = form_search.cleaned_data['end_time']
        device = form_search.cleaned_data['device']
        exposure_time = form_search.cleaned_data['exposure_time']
        aperture_value = form_search.cleaned_data['aperture_value']
        ISO_speed = form_search.cleaned_data['ISO_speed']
        toShow = SkyPicture.objects.filter(exposure_time__in = exposure_time,
             aperture_value__in = aperture_value, ISO_speed__in = ISO_speed, device = device
             ).exclude(date__gt = end_date).exclude(date__lt = start_date
             ).exclude(time__gt = end_time).exclude(time__lt = start_time
             ).order_by('-date','-time')
    else:
        toShow = SkyPicture.objects.all().order_by('-date','-time')
        
    # Create a paginator for displaying images 10 by 10
    paginator = Paginator(toShow, 10)
    try:
        toShow = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        toShow = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        toShow = paginator.page(paginator.num_pages)
    
    args['form_search'] = form_search
    args['title'] = "Sky pictures"
    args['results'] = toShow
    
    if MeasuringDevice.objects.filter(type = 'W').exists() & SkyPicture.objects.exists():
        args['data_available'] = True
    else:
        args['data_available'] = False
    
    return render(request, 'picture_browser/index.html', args)
