# -*- coding: utf-8 -*-
#

from django.db import models
from django.utils.translation import ugettext as _

from .base import AssetUser
from orgs.mixins import OrgManager

__all__ = ['AuthBook']


class AuthBookQuerySet(models.QuerySet):

    def latest_version(self):
        return self.filter(is_latest=True)


class AuthBookManager(OrgManager):
    pass


class AuthBook(AssetUser):
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, verbose_name=_('Asset'))
    is_latest = models.BooleanField(default=False, verbose_name=_('Latest'))
    version_count = models.IntegerField(default=1, verbose_name=_('Version count'))

    objects = AuthBookManager.from_queryset(AuthBookQuerySet)()

    class Meta:
        verbose_name = _('Auth book')

    def _set_latest(self):
        self._remove_pre_obj_latest()
        self.is_latest = True
        self.save()

    def _get_pre_obj(self):
        pre_obj = self.__class__.objects.filter(
            username=self.username, asset=self.asset).latest_version().first()
        return pre_obj

    def _remove_pre_obj_latest(self):
        pre_obj = self._get_pre_obj()
        if pre_obj:
            pre_obj.is_latest = False
            pre_obj.save()

    def _set_version_count(self):
        pre_obj = self._get_pre_obj()
        if pre_obj:
            self.version_count = pre_obj.version_count + 1
        else:
            self.version_count = 1

    def set_latest(self):
        self._set_latest()
        self._set_version_count()

    @property
    def keyword(self):
        return {'username': self.username, 'asset': self.asset}

    def __str__(self):
        return '{}@{}'.format(self.username, self.asset)

