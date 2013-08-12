# file battleofatlanta/apps/tour/models.py

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf import settings

# third party imports
from autoslug import AutoSlugField
from tinymce.models import HTMLField
from PIL import Image

import re
import os
import magic
from cStringIO import StringIO

class Tour(models.Model):
    name = models.CharField(max_length=50)
    description = HTMLField()
    slug = AutoSlugField(populate_from='name', unique=True)

    class Meta:
        verbose_name = _('Tour')
        verbose_name_plural = _('Tours')

    def __unicode__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse('detail', kwargs={'slug': self.slug})

class TourStopMediaType(models.Model):
    title = models.CharField(max_length=50)

    def __unicode__(self):
        return "%s" % (self.title)

class TourStop(models.Model):
    tour = models.ForeignKey(Tour)
    name = models.CharField(max_length=50)
    description = HTMLField(blank=True, default='')
    description_brief = HTMLField(blank=True, default='')

    # geo fields
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    # used in drag and drop reodering as well as tour stop order
    position = models.PositiveSmallIntegerField("Position", default=12)

    class Meta:
        verbose_name = _('Tour Stop')
        verbose_name_plural = _('Tour Stops')

        #set default ordering for the manager
        ordering = ['position']

    def __unicode__(self):
        return "%s - %s" % (self.name, self.tour.name)

    def get_absolute_url(self):
        return reverse('tour:stop-detail', kwargs={"slug":  self.tour.slug, "page": self.position + 1})

    @property
    def slug(self):
        return slugify(self.name)

# callback for tour_stop image name
def tour_stop_image_filename(instance, filename):
    fname, ext = os.path.splitext(filename)
    return '/'.join(['tour_stops', instance.tour_stop.slug, "%s%s" % (slugify(fname), ext)])

# callback for the thumbnail path
def tour_stop_thumb_filename(instance, filename):
    fname, ext = os.path.splitext(filename)
    return '/'.join(['tour_stops', instance.tour_stop.slug,'thumbs', "%s%s" % (slugify(fname), ext)])

def tour_splash_image_filename(instance, filename):
    fname, ext = os.path.splitext(filename)
    return '/'.join(['tours', instance.tour_stop.slug, "%s%s" % (slugify(fname), ext)])

class TourStopMedia(models.Model):
    tour_stop = models.ForeignKey(TourStop)
    media_type = models.ForeignKey(TourStopMediaType, default='1')
    title = models.CharField(max_length=50, blank=True, default='')
    caption = models.CharField(max_length=255, blank=True, default='')
    image = models.FileField(upload_to=tour_stop_image_filename, blank=True, default='')
    thumbnail = models.ImageField(upload_to=tour_stop_thumb_filename, blank=True, default='')

    class Meta:
        verbose_name = _('Tour Stop Media')
        verbose_name_plural = _('Tour Stop Media')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tour:stop-media-detail', kwargs={"slug":  self.tour_stop.tour.slug, "id": self.id})

    def save(self, force_update=False, force_insert=False):
        orig = None
	print("self.pk = %s" % self.pk)
        if self.pk is not None:
            orig = TourStopMedia.objects.get(pk=self.pk)
   	    print("orig = %s" % orig) 
        # finally we save the TSMedia object
        super(TourStopMedia, self).save(force_update, force_insert)

        type = magic.from_file(getattr(settings, "MEDIA_ROOT", None) + '/' + str(self.image))
        print(type)

        if re.search('image', type):
    
            if not self.thumbnail or (orig and self.image != orig.image):
                print "creating thumbnail"
                #create thumbnail if it doesn't exist
                image = Image.open(self.image)
    
                # retrieve original size for computation of thumb size
                width, height = image.size
    
                #compute thumb size currently hardcoded to maintain aspect ratio with 125px width
                # TODO: refactor to class variable
                thumb_w = 125
                thumb_h = height * thumb_w / width
    
                image.thumbnail((thumb_w, thumb_h), Image.ANTIALIAS)
    
                # save the thumbnail to memory
                temp_handle = StringIO()
                image.save(temp_handle, image.format)
                temp_handle.seek(0) #rewind the file
    
                # save the thumbnail field
                suf = SimpleUploadedFile(os.path.split(self.image.name)[-1],
                                         temp_handle.read(),
                                        content_type='image/%s' % image.format)
                self.thumbnail.save(suf.name, suf, save=False)

        # finally we save the TSMedia object
        super(TourStopMedia, self).save(force_update, force_insert)

class TourSplashImage(models.Model):
	tour = models.ForeignKey(Tour)
	splashimage = models.ImageField(upload_to='tours/', blank=True, default='')

	def save(self, force_update=False, force_insert=False):

		#super(TourSplashImage, self).save()
		image = Image.open(self.splashimage)

		width = 290
		height = 190

		image.thumbnail((width, height), Image.ANTIALIAS)
		image.save(self.splashimage.path)

		# save the thumbnail to memory
		temp_handle = StringIO()
		image.save(temp_handle, image.format)
		temp_handle.seek(0) #rewind the file

		suf = SimpleUploadedFile(os.path.split(self.splashimage.name)[-1],
					temp_handle.read(),
					content_type='image/%s' % image.format)
		self.splashimage.save(suf.name, suf, save=False)
		super(TourSplashImage, self).save()
