# -*- coding: utf-8 -*-
#
# Project Ginger
#
# Copyright IBM Corp, 2016-2017
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import errno
import hashlib
import itertools
import os
import re
import time
import uuid

import cherrypy

from wok.asynctask import AsyncTask
from wok.config import PluginPaths
from wok.exception import InvalidOperation, NotFoundError, OperationFailed
from wok.exception import InvalidParameter
from wok.model.tasks import TaskModel
from wok.utils import run_command, wok_log


class BackupModel(object):

    def __init__(self, **kargs):
        self._objstore = kargs['objstore']
        self._archives_model = ArchivesModel(**kargs)
        self._archive_model = ArchiveModel(**kargs)

    def _get_archives_to_discard(self, archives, days_ago, counts_ago):
        try:
            days_ago = int(days_ago)
        except ValueError:
            raise InvalidParameter('GINHBK0007E')
        try:
            counts_ago = int(counts_ago)
        except ValueError:
            raise InvalidParameter('GINHBK0008E')
        if days_ago == 0 or counts_ago == 0:
            return archives[:]

        to_remove = []

        # Older archive comes first.
        archives.sort(lambda l, r: cmp(l['timestamp'], r['timestamp']))

        if counts_ago != -1:
            to_remove.extend(archives[:-counts_ago])
            archives = archives[-counts_ago:]

        if days_ago != -1:
            expire = time.time() - 3600 * 24 * days_ago
            to_remove.extend(
                itertools.takewhile(
                    lambda ar: ar['timestamp'] < expire, archives))

        return to_remove

    def discard_archives(self, _ident, days_ago=-1, counts_ago=-1):
        ''' Discard archives older than some days ago, or some counts ago. '''
        try:
            days_ago = int(days_ago)
        except ValueError:
            raise InvalidParameter('GINHBK0007E')
        try:
            counts_ago = int(counts_ago)
        except ValueError:
            raise InvalidParameter('GINHBK0008E')

        with self._objstore as session:
            archives = [
                session.get(ArchivesModel._objstore_type, ar_id)
                for ar_id in self._archives_model._session_get_list(session)]

            to_remove = self._get_archives_to_discard(
                archives, days_ago, counts_ago)

            for ar in to_remove:
                self._archive_model._session_delete_archive(session,
                                                            ar['identity'])


def get_tar_create_timeout():
    return int(cherrypy.request.app.config['backup']['timeout'])


def _tar_create_archive(directory_path, archive_id, include, exclude_flag):
    archive_file = os.path.join(directory_path, archive_id + '.tar.gz')
    backup_dir = os.path.join(PluginPaths('ginger').state_dir,
                              'ginger_backups')

    bkp = re.compile(backup_dir)
    if filter(bkp.match, include) and (len(include) == 1):
        raise InvalidOperation('GINHBK0012E', {'dir': backup_dir})

    exclude = ['--exclude=' + backup_dir]
    if exclude_flag:
        exclude.extend(['--exclude=' + toExclude for toExclude in
                        exclude_flag])
    cmd = ['tar', '--create', '--ignore-failed-read', '--gzip',
           '--absolute-names', '--file', archive_file, '--selinux', '--acl',
           '--xattrs'] + exclude + include
    out, err, rc = run_command(cmd)
    if rc != 0:
        if 'file changed as we read it' in err:
            raise OperationFailed('GINHBK0010E', {'file': err.split(': ')[1]})
        raise OperationFailed('GINHBK0001E', {'name': archive_file,
                                              'cmd': ' '.join(cmd)})

    return archive_file


def _sha256sum(filename):
    sha = hashlib.sha256()
    with open(filename, 'rb') as f:
        for c in iter(lambda: f.read(131072), ''):
            sha.update(c)
    return sha.hexdigest()


class ArchivesModel(object):
    _objstore_type = 'ginger_backup_archive'
    _archive_dir = os.path.join(PluginPaths('ginger').state_dir,
                                'ginger_backups')

    def __init__(self, **kargs):
        self._objstore = kargs['objstore']
        self.task = TaskModel(**kargs)
        self._create_archive_dir()

    @classmethod
    def _create_archive_dir(cls):
        try:
            os.makedirs(cls._archive_dir)
        except OSError as e:
            # It's OK if archive_dir already exists
            if e.errno != errno.EEXIST:
                wok_log.error('Error creating archive dir %s: %s',
                              cls._archive_dir, e)
                raise OperationFailed('GINHBK0003E',
                                      {'dir': cls._archive_dir})

    @property
    def _default_include(self):
        # This function builds a new copy of the list for each invocation,
        # so that the caller can modify the returned list as wish without
        # worrying about changing the original reference.
        return list(cherrypy.request.app.config['backup']['default_include'])

    @property
    def _default_exclude(self):
        # See _default_include() comments for explanation.
        return list(cherrypy.request.app.config['backup']['default_exclude'])

    def _create_archive(self, params):
        error = None
        try:
            params['file'] = _tar_create_archive(self._archive_dir,
                                                 params['identity'],
                                                 params['include'],
                                                 params['exclude'])
            params['checksum'] = {'algorithm': 'sha256',
                                  'value': _sha256sum(params['file'])}

            with self._objstore as session:
                session.store(self._objstore_type, params['identity'], params)
        except InvalidOperation:
            raise
        except OperationFailed:
            raise
        except Exception as e:
            error = e
            reason = 'GINHBK0009E'

        if error is not None:
            msg = 'Error creating archive %s: %s' % (params['identity'],
                                                     error.message)
            wok_log.error(msg)

            try:
                with self._objstore as session:
                    session.delete(self._objstore_type, params['identity'],
                                   ignore_missing=True)
            except Exception as e_session:
                wok_log.error('Error cleaning archive meta data %s. '
                              'Error: %s', params['identity'], e_session)

            if params['file'] != '':
                try:
                    os.unlink(params['file'])
                except Exception as e_file:
                    wok_log.error('Error cleaning archive file %s. '
                                  'Error: %s', params['file'], e_file)

            raise OperationFailed(reason, {'identity': params['identity']})

    def create(self, params):
        uuid_uuid4 = uuid.uuid4()
        if isinstance(uuid_uuid4, unicode):
            uuid_uuid4 = uuid_uuid4.encode('utf-8')
        archive_id = str(uuid_uuid4)
        stamp = int(time.mktime(time.localtime()))

        # Though formally we ask front-end to not send "include" at all when
        # it's empty, but in implementation we try to be tolerant.
        # Front-end can also send [] to indicate the "include" is empty.
        include = params.get('include')
        exclude = params.get('exclude', [])
        if not include:
            include = self._default_include
            if not exclude:
                exclude = self._default_exclude

        ar_params = {'identity': archive_id,
                     'include': include,
                     'exclude': exclude,
                     'description': params.get('description', ''),
                     'checksum': {},
                     'timestamp': stamp,
                     'file': ''}

        taskid = AsyncTask(u'/backup/create/%s' % (archive_id),
                           self._create_task, ar_params).id
        return self.task.lookup(taskid)

    def _create_task(self, cb, params):

        cb('entering task to create config backup')
        try:
            self._create_archive(params)
            cb('OK', True)
        except (InvalidOperation) as e:
            cb(e.message, False)
        except (OperationFailed) as e:
            cb(e.message, False)
            raise OperationFailed('GINHBK0011E',
                                  {'params': 'params',
                                   'err': e.message})

    def _session_get_list(self, session):
        # Assume session is already locked.
        return session.get_list(self._objstore_type, sort_key='timestamp')

    def get_list(self):
        with self._objstore as session:
            files = [x.split('.')[0] for x in os.listdir(self._archive_dir)]
            for db_file in self._session_get_list(session):
                if db_file not in files:
                    session.delete(ArchivesModel._objstore_type, db_file)
            return self._session_get_list(session)


class ArchiveModel(object):

    def __init__(self, **kargs):
        self._objstore = kargs['objstore']
        self.task = TaskModel(**kargs)

    def lookup(self, archive_id):
        with self._objstore as session:
            info = session.get(ArchivesModel._objstore_type, archive_id)
        return info

    def _session_delete_archive(self, session, archive_id):
        # Assume session is already locked.
        try:
            ar_params = session.get(ArchivesModel._objstore_type, archive_id)
        except NotFoundError:
            return

        if ar_params['file'] != '':
            try:
                os.unlink(ar_params['file'])
            except OSError as e:
                # It's OK if the user already removed the file manually
                if e.errno not in (errno.EACCES, errno.ENOENT):
                    raise OperationFailed(
                        'GINHBK0002E', {'name': ar_params['file']})

        session.delete(ArchivesModel._objstore_type, archive_id)

    def delete(self, archive_id):
        with self._objstore as session:
            self._session_delete_archive(session, archive_id)

    def _restore_tar(self, archive_id):
        backup_dir = os.path.join(PluginPaths('ginger').state_dir,
                                  'ginger_backups')
        backup_file = os.path.join(backup_dir, archive_id + '.tar.gz')
        cmd = ['tar', '-xzf', backup_file, '-C', '/']
        out, err, rc = run_command(cmd)
        if rc != 0:
            raise OperationFailed('GINHBK0001E', {'name': backup_file,
                                                  'cmd': ' '.join(cmd)})

    def _restore_task(self, rb, backup_id):
        rb('entering task to restore config backup')
        try:
            self._restore_tar(backup_id)
            rb('OK', True)
        except (InvalidOperation) as e:
            rb(e.message, False)
        except (OperationFailed) as e:
            rb(e.message, False)
            raise OperationFailed('GINHBK0013E', {'err': e.message})

    def restore(self, archive_id):
        taskid = AsyncTask(u'/backup/restore/%s' % (archive_id),
                           self._restore_task, archive_id).id
        return self.task.lookup(taskid)
