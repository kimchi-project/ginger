#
# Ginger
#
# Copyright IBM Corp, 2014
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

SUBDIRS= po controls models ui

ACLOCAL_AMFLAGS = --install -I m4

PEP8_WHITELIST = \
	controls \
	models \
	$(NULL)

ginger_PYTHON = \
	__init__.py \
	ginger.py \
	i18n.py \
	$(NULL)

gingerdir = $(pythondir)/kimchi/plugins/ginger

confdir = $(sysconfdir)/kimchi/plugins.d
dist_conf_DATA = ginger.conf

EXTRA_DIST = \
	API.json \
	VERSION \
	build-aux/config.rpath \
	build-aux/pkg-version \
	$(NULL)

CLEANFILES = \
	$(ginger_PYTHON:%.py=%.pyc) \
	$(NULL)


check-local:
	find . -path './.git' -prune -type f -o \
		-name '*.py' -o -name '*.py.in'  | xargs $(PYFLAKES) | \
		while read LINE; do echo "$$LINE"; false; done
	$(PEP8) --version
	$(PEP8) --filename '*.py,*.py.in' $(PEP8_WHITELIST)


# Link built mo files in the source tree to enable use of translations from
# within the source tree
all-local:
	while read L && test -n "$$L"; do                  \
		dir=mo/$$L/LC_MESSAGES ;                       \
		$(MKDIR_P) $$dir ;                             \
		ln -sf ../../../po/$$L.gmo $$dir/ginger.mo ;   \
	done < po/LINGUAS


install-data-local:
	$(MKDIR_P) $(DESTDIR)$(gingerdir)
	$(INSTALL_DATA) API.json $(DESTDIR)$(gingerdir)/API.json


rpm: dist ginger.spec
	$(MKDIR_P) rpm/BUILD rpm/RPMS rpm/SOURCES rpm/SPECS rpm/SRPMS
	cp $(top_srcdir)/ginger.spec rpm/SPECS/ginger.spec
	cp $(DIST_ARCHIVES) rpm/SOURCES
	rpmbuild -ba --define "_topdir `pwd`/rpm" rpm/SPECS/ginger.spec


ChangeLog:
	@if test -d .git; then                                   \
		$(top_srcdir)/build-aux/genChangelog --release > $@; \
	fi


VERSION:
	@if test -d .git; then                                \
		git describe --abbrev=0 > $@;                     \
	fi


clean-local:
	rm -rf rpm


.PHONY: rpm ChangeLog VERSION
